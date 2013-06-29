'''
Selection
=========

.. versionadded:: 1.8

.. warning::

    This code is still experimental, and its API is subject to change in a
    future version.

:class:`Selection` contains a selection support system for
:class:`ListProperty` and related collection properties.

It is inpired by SproutCore's SC.SelectionSupport mixin.

TODO: SC.SelectionSupport has allow_multple_selection, has_selection_support,
      allows_selection, has_selection, first_selectable_object. Consider the
      use of these, for possible inclusion here.

Selection operations are the main concern for the class.

* *selection*, a list of selected items.

* *selection_mode*, 'single', 'multiple', 'none'

* *allow_empty_selection*, a boolean -- If False, a selection is forced. If
  True, and only user or programmatic action will change selection, it can
  be empty.

Classes which mix in :class:`Selection` should implement dispatching the
*on_selection_change* event.

    :Events:
        `on_selection_change`: (item proxy, item proxies list )
            Fired when selection changes
'''

__all__ = ('Selection', )

import inspect
from kivy.event import EventDispatcher
from kivy.adapters.models import SelectableDataItem
from kivy.properties import ListProperty
from kivy.properties import DictProperty
from kivy.properties import BooleanProperty
from kivy.properties import OptionProperty
from kivy.properties import NumericProperty


class Proxy(object):
    pass


class Selection(EventDispatcher):
    '''
    A base class for interfacing with lists, dictionaries or other
    collection type data, adding selection and management functonality.
    '''

    data = ListProperty([])
    '''The data list property is bound so that changes will trigger updates.

    :data:`data` is a :class:`~kivy.properties.ListProperty` and defaults
    to [].
    '''

    selection = ListProperty([])
    '''The selection list property is the container for selected items.

    :data:`selection` is a :class:`~kivy.properties.ListProperty` and defaults
    to [].
    '''

    selection_mode = OptionProperty('single',
            options=('none', 'single', 'multiple'))
    '''Selection modes:

       * *none*, use the list as a simple list (no select action). This option
         is here so that selection can be turned off, momentarily or
         permanently, for an existing list adapter.
         A :class:`~kivy.adapters.listadapter.ListAdapter` is not meant to be
         used as a primary no-selection list adapter.  Use a
         :class:`~kivy.adapters.simplelistadapter.SimpleListAdapter` for that.

       * *single*, multi-touch/click ignored. Single item selection only.

       * *multiple*, multi-touch / incremental addition to selection allowed;
         may be limited to a count by selection_limit

    :data:`selection_mode` is an :class:`~kivy.properties.OptionProperty` and
    defaults to 'single'.
    '''

    propagate_selection_to_data = BooleanProperty(False)
    '''Normally, data items are not selected/deselected because the data items
    might not have an is_selected boolean property -- only the proxy for a
    given data item is selected/deselected as part of the maintained selection
    list. However, if the data items do have an is_selected property, or if
    they mix in :class:`~kivy.adapters.models.SelectableDataItem`, the
    selection machinery can propagate selection to data items. This can be
    useful for storing selection state in a local database or backend database
    for maintaining state in game play or other similar scenarios. It is a
    convenience function.

    To propagate selection or not?

    Consider a shopping list application for shopping for fruits at the market.
    The app allows for the selection of fruits to buy for each day of the week,
    presenting seven lists: one for each day of the week. Each list is loaded
    with all the available fruits, but the selection for each is a subset.
    There is only one set of fruit data shared between the lists, so it would
    not make sense to propagate selection to the data because selection in any
    of the seven lists would clash and mix with that of the others.

    However, consider a game that uses the same fruits data for selecting
    fruits available for fruit-tossing. A given round of play could have a
    full fruits list, with fruits available for tossing shown selected. If the
    game is saved and rerun, the full fruits list, with selection marked on
    each item, would be reloaded correctly if selection is always propagated to
    the data. You could accomplish the same functionality by writing code to
    operate on list selection, but having selection stored in the data
    ListProperty might prove convenient in some cases.

    :data:`propagate_selection_to_data` is a
    :class:`~kivy.properties.BooleanProperty` and defaults to False.
    '''

    allow_empty_selection = BooleanProperty(True)
    '''The allow_empty_selection property may be set to False so that the
    selection is auto-initialized and always maintained, so any observing views
    may likewise be updated to stay in sync.

    allow_empty_selection may be used for cascading selection between several
    list, or between a list and an observing view. Such automatic maintenance
    of the selection is important for all but simple list displays.

    :data:`allow_empty_selection` is a
    :class:`~kivy.properties.BooleanProperty` and defaults to True.
    '''

    selection_limit = NumericProperty(-1)
    '''When the selection_mode is multiple and the selection_limit is
    non-negative, this number will limit the number of selected items. It can
    be set to 1, which is equivalent to single selection. If selection_limit is
    not set, the default value is -1, meaning that no limit will be enforced.

    :data:`selection_limit` is a :class:`~kivy.properties.NumericProperty` and
    defaults to -1 (no limit).
    '''

    cached_views = DictProperty({})
    '''View instances for data items are instantiated and managed by the
    adapter. Here we maintain a dictionary containing the view
    instances keyed to the indices in the data.

    This dictionary works as a cache. get_view() only asks for a view from
    the adapter if one is not already stored for the requested index.

    :data:`cached_views` is a :class:`~kivy.properties.DictProperty` and
    defaults to {}.
    '''

    __events__ = ('on_selection_change', )

    def __init__(self, **kwargs):
        super(Selection, self).__init__(**kwargs)

        self.bind(selection_mode=self.selection_mode_changed,
                  allow_empty_selection=self.check_for_empty_selection,
                  data=self.update_for_new_data)

        self.update_for_new_data()

    def delete_cache(self, *args):
        self.cached_views = {}

    def get_count(self):
        return len(self.data)

    def get_data_item(self, index):
        if index < 0 or index >= len(self.data):
            return None
        return self.data[index]

    def selection_mode_changed(self, *args):
        if self.selection_mode == 'none':
            for selected_proxy in self.selection:
                self.deselect_item_proxy(selected_proxy)
        else:
            self.check_for_empty_selection()

    # TODO: get_proxy()? And tie in the parent class view creation and
    #       destruction? Proxy contains links to views? Cached proxies
    #       which link to cached views?
    def get_view(self, index):
        if index in self.cached_views:
            return self.cached_views[index]
        item_view = self.create_view(index)
        if item_view:
            self.cached_views[index] = item_view
        return item_view

    def create_proxy(self, index):
        '''This method is more complicated than the one in
        :class:`kivy.adapters.adapter.Adapter` and
        :class:`kivy.adapters.simplelistadapter.SimpleListAdapter`, because
        here we create bindings for the data item and its children back to
        self.handle_selection(), and do other selection-related tasks to keep
        item proxies in sync with the data.
        '''
        item = self.get_data_item(index)
        if item is None:
            return None

        item_args = self.args_converter(index, item)

        item_args['index'] = index

        proxy_instance = Proxy()

        if self.propagate_selection_to_data:
            # The data item must be a subclass of SelectableDataItem, or must
            # have an is_selected boolean or function, so it has is_selected
            # available.  If is_selected is unavailable on the data item, an
            # exception is raised.
            #
            if isinstance(item, SelectableDataItem):
                if item.is_selected:
                    self.handle_selection(proxy_instance)
            elif type(item) == dict and 'is_selected' in item:
                if item['is_selected']:
                    self.handle_selection(proxy_instance)
            elif hasattr(item, 'is_selected'):
                if (inspect.isfunction(item.is_selected)
                        or inspect.ismethod(item.is_selected)):
                    if item.is_selected():
                        self.handle_selection(proxy_instance)
                else:
                    if item.is_selected:
                        self.handle_selection(proxy_instance)
            else:
                msg = "ListAdapter: unselectable data item for {0}"
                raise Exception(msg.format(index))

        proxy_instance.bind(on_release=self.handle_selection)

        for child in proxy_instance.children:
            child.bind(on_release=self.handle_selection)

        return proxy_instance

    def on_selection_change(self, *args):
        '''on_selection_change() is the default handler for the
        on_selection_change event.
        '''
        pass

    def update_for_new_data(self, *args):
        self.delete_cache()
        self.initialize_selection()

    def handle_selection(self, proxy_instance, hold_dispatch=False, *args):
        if proxy_instance not in self.selection:
            if self.selection_mode in ['none', 'single'] and \
                    len(self.selection) > 0:
                for selected_proxy in self.selection:
                    self.deselect_item_proxy(selected_proxy)
            if self.selection_mode != 'none':
                if self.selection_mode == 'multiple':
                    if self.allow_empty_selection:
                        # If < 0, selection_limit is not active.
                        if self.selection_limit < 0:
                            self.select_item_proxy(proxy_instance)
                        else:
                            if len(self.selection) < self.selection_limit:
                                self.select_item_proxy(proxy_instance)
                    else:
                        self.select_item_proxy(proxy_instance)
                else:
                    self.select_item_proxy(proxy_instance)
        else:
            self.deselect_item_proxy(proxy_instance)
            if self.selection_mode != 'none':
                # If the deselection makes selection empty, the following call
                # will check allows_empty_selection, and if False, will select
                # the first item. If proxy_instance happens to be the first
                # item, this will be a reselection, and the user will notice no
                # change, except perhaps a flicker.
                #
                self.check_for_empty_selection()

        if not hold_dispatch:
            self.dispatch('on_selection_change')

    def select_data_item(self, item):
        self.set_data_item_selection(item, True)

    def deselect_data_item(self, item):
        self.set_data_item_selection(item, False)

    def set_data_item_selection(self, item, value):
        if isinstance(item, SelectableDataItem):
            item.is_selected = value
        elif type(item) == dict:
            item['is_selected'] = value
        elif hasattr(item, 'is_selected'):
            if (inspect.isfunction(item.is_selected)
                    or inspect.ismethod(item.is_selected)):
                item.is_selected()
            else:
                item.is_selected = value

    def select_item_proxy(self, proxy):
        proxy.select()
        proxy.is_selected = True
        self.selection.append(proxy)

        if self.propagate_selection_to_data:
            data_item = self.get_data_item(proxy.index)
            self.select_data_item(data_item)

    def select_list(self, proxies, extend=True):
        '''The select call is made for the items in the provided proxies.

        Arguments:

            proxies: the list of item proxies to become the new selection, or
            to add to the existing selection

            extend: boolean for whether or not to extend the existing list
        '''
        if not extend:
            self.selection = []

        for proxy in proxies:
            self.handle_selection(proxy, hold_dispatch=True)

        self.dispatch('on_selection_change')

    def deselect_item_proxy(self, proxy):
        proxy.deselect()
        proxy.is_selected = False
        self.selection.remove(proxy)

        if self.propagate_selection_to_data:
            item = self.get_data_item(proxy.index)
            self.deselect_data_item(item)

    def deselect_list(self, proxies):
        for proxy in proxies:
            self.handle_selection(proxy, hold_dispatch=True)

        self.dispatch('on_selection_change')

    # [TODO] Could easily add select_all() and deselect_all().

    def initialize_selection(self, *args):
        if len(self.selection) > 0:
            self.selection = []
            self.dispatch('on_selection_change')

        self.check_for_empty_selection()

    def check_for_empty_selection(self, *args):
        if not self.allow_empty_selection:
            if len(self.selection) == 0:
                # Select the first item if we have it.
                proxy = self.get_proxy(0)
                if proxy is not None:
                    self.handle_selection(proxy)

    def trim_left_of_sel(self, *args):
        '''Cut items with indices that are less than the index of the first
        selected item if there is a selection.
        '''
        if len(self.selection) > 0:
            first_sel_index = min([sel.index for sel in self.selection])
            self.data = self.data[first_sel_index:]

    def trim_right_of_sel(self, *args):
        '''Cut items with indices that are greater than the index of the last
        selected item if there is a selection.
        '''
        if len(self.selection) > 0:
            last_sel_index = max([sel.index for sel in self.selection])
            self.data = self.data[:last_sel_index + 1]

    def trim_to_sel(self, *args):
        '''Cut items with indices that are les than or greater than the index
        of the last selected item if there is a selection. This preserves
        intervening list items within the selected range.
        '''
        if len(self.selection) > 0:
            sel_indices = [sel.index for sel in self.selection]
            first_sel_index = min(sel_indices)
            last_sel_index = max(sel_indices)
            self.data = self.data[first_sel_index:last_sel_index + 1]

    def cut_to_sel(self, *args):
        '''Same as trim_to_sel, but intervening items within the selected range
        are also cut, leaving only items that are selected.
        '''
        if len(self.selection) > 0:
            self.data = self.selection
