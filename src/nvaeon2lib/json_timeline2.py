"""Provide a class for Aeon Timeline 2 JSON representation.

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/aeon2nv
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
from datetime import datetime
from datetime import timedelta
from novxlib.novx_globals import *
from novxlib.model.chapter import Chapter
from novxlib.model.scene import Scene
from novxlib.model.character import Character
from novxlib.model.world_element import WorldElement
from novxlib.model.novel import Novel
from novxlib.model.id_generator import create_id
from novxlib.file.file import File
from nvaeon2lib.aeon2_fop import open_timeline
from nvaeon2lib.aeon2_fop import save_timeline
from nvaeon2lib.uid_helper import get_uid
from nvaeon2lib.moonphase import get_moon_phase_plus


class JsonTimeline2(File):
    """File representation of an Aeon Timeline 2 project. 

    Public methods:
        read() -- parse the file and get the instance variables.
        merge(source) -- update instance variables from a source instance.
        write() -- write instance variables to the file.

    Public class constants:
        SCN_KWVAR -- List of the names of the scene keyword variables.
        CRT_KWVAR -- List of the names of the character keyword variables.
    
    Represents the .aeonzip file containing 'timeline.json'.
    """
    EXTENSION = '.aeonzip'
    DESCRIPTION = _('Aeon Timeline 2 project')
    SUFFIX = ''
    VALUE_YES = '1'
    # JSON representation of "yes" in Aeon2 "yes/no" properties
    DATE_LIMIT = (datetime(100, 1, 1) - datetime.min).total_seconds()
    # Dates before 100-01-01 can not be displayed properly in novelyst
    PROPERTY_MOONPHASE = 'Moon phase'

    SCN_KWVAR = [
        'Field_SceneArcs',
        ]
    CRT_KWVAR = [
        'Field_BirthDate',
        'Field_DeathDate',
        ]

    def __init__(self, filePath, **kwargs):
        """Initialize instance variables.

        Positional arguments:
            filePath: str -- path to the file represented by the File instance.
            
        Required keyword arguments:
            narrative_arc: str -- name of the user-defined "Narrative" arc.
            property_description: str -- name of the user-defined scene description property.
            property_notes: str -- name of the user-defined scene notes property.
            role_location: str -- name of the user-defined role for scene locations.
            role_item: str -- name of the user-defined role for items in a scene.
            role_character: str -- name of the user-defined role for characters in a scene.
            type_character: str -- name of the user-defined "Character" type.
            type_location: str -- name of the user-defined "Location" type.
            type_item: str -- name of the user-defined "Item" type.
            scenes_only: bool -- synchronize only "Normal" scenes.
            color_scene: str -- color of new scene events.
            color_event: str -- color of new non-scene events.
            add_moonphase: bool -- add a moon phase property to each event.
        
        If scenes_only is True: synchronize only "Normal" scenes.
        If scenes_only is False: synchronize "Notes" scenes as well.            
        Extends the superclass constructor.
        """
        super().__init__(filePath, **kwargs)
        self._jsonData = None

        # JSON[entities][name]
        self._entityNarrative = kwargs['narrative_arc']

        # JSON[template][properties][name]
        self._propertyDesc = kwargs['property_description']
        self._propertyNotes = kwargs['property_notes']

        # JSON[template][types][name][roles]
        self._roleLocation = kwargs['role_location']
        self._roleItem = kwargs['role_item']
        self._roleCharacter = kwargs['role_character']

        # JSON[template][types][name]
        self._typeCharacter = kwargs['type_character']
        self._typeLocation = kwargs['type_location']
        self._typeItem = kwargs['type_item']

        # GUIDs
        self._tplDateGuid = None
        self._typeArcGuid = None
        self._typeCharacterGuid = None
        self._typeLocationGuid = None
        self._typeItemGuid = None
        self._roleArcGuid = None
        self._roleStorylineGuid = None
        self._roleCharacterGuid = None
        self._roleLocationGuid = None
        self._roleItemGuid = None
        self._entityNarrativeGuid = None
        self._propertyDescGuid = None
        self._propertyNotesGuid = None
        self._propertyMoonphaseGuid = None

        # Miscellaneous
        self.referenceDateStr = kwargs['default_date_time']
        try:
            self.referenceDate = datetime.fromisoformat(self.referenceDateStr)
        except ValueError:
            self.referenceDate = datetime.today()
        self._scenesOnly = kwargs['scenes_only']
        self._addMoonphase = kwargs['add_moonphase']
        self._sceneColor = kwargs['color_scene']
        self._eventColor = kwargs['color_event']
        self._pointColor = kwargs['color_point']
        self._timestampMax = 0
        self._displayIdMax = 0.0
        self._colors = {}
        self._arcCount = 0
        self._characterGuidById = {}
        self._locationGuidById = {}
        self._itemGuidById = {}
        self._trashEvents = []
        self._arcGuidsByName = {}

    def read(self):
        """Parse the file and get the instance variables.
        
        Read the JSON part of the Aeon Timeline 2 file located at filePath, 
        and build a novelyst novel structure.
        - Events marked as scenes are converted to scenes in one single chapter.
        - Other events are converted to "Notes" scenes in another chapter.
        Raise the "Error" exception in case of error. 
        Overrides the superclass method.
        """
        self._jsonData = open_timeline(self.filePath)

        #--- Get the color definitions.
        for tplCol in self._jsonData['template']['colors']:
            self._colors[tplCol['name']] = tplCol['guid']

        #--- Get the date definition.
        for tplRgp in self._jsonData['template']['rangeProperties']:
            if tplRgp['type'] == 'date':
                for tplRgpCalEra in tplRgp['calendar']['eras']:
                    if tplRgpCalEra['name'] == 'AD':
                        self._tplDateGuid = tplRgp['guid']
                        break

        if self._tplDateGuid is None:
            raise Error(_('"AD" era is missing in the calendar.'))

        #--- Get GUID of user defined types and roles.
        for tplTyp in self._jsonData['template']['types']:
            if tplTyp['name'] == 'Arc':
                self._typeArcGuid = tplTyp['guid']
                for tplTypRol in tplTyp['roles']:
                    if tplTypRol['name'] == 'Arc':
                        self._roleArcGuid = tplTypRol['guid']
                    elif tplTypRol['name'] == 'Storyline':
                        self._roleStorylineGuid = tplTypRol['guid']
            elif tplTyp['name'] == self._typeCharacter:
                self._typeCharacterGuid = tplTyp['guid']
                for tplTypRol in tplTyp['roles']:
                    if tplTypRol['name'] == self._roleCharacter:
                        self._roleCharacterGuid = tplTypRol['guid']
            elif tplTyp['name'] == self._typeLocation:
                self._typeLocationGuid = tplTyp['guid']
                for tplTypRol in tplTyp['roles']:
                    if tplTypRol['name'] == self._roleLocation:
                        self._roleLocationGuid = tplTypRol['guid']
                        break

            elif tplTyp['name'] == self._typeItem:
                self._typeItemGuid = tplTyp['guid']
                for tplTypRol in tplTyp['roles']:
                    if tplTypRol['name'] == self._roleItem:
                        self._roleItemGuid = tplTypRol['guid']
                        break

        #--- Add "Arc" type, if missing.
        if self._typeArcGuid is None:
            self._typeArcGuid = get_uid('typeArcGuid')
            typeCount = len(self._jsonData['template']['types'])
            self._jsonData['template']['types'].append(
                {
                    'color': 'iconYellow',
                    'guid': self._typeArcGuid,
                    'icon': 'book',
                    'name': 'Arc',
                    'persistent': True,
                    'roles': [],
                    'sortOrder': typeCount
                })
        for entityType in self._jsonData['template']['types']:
            if entityType['name'] == 'Arc':
                if self._roleArcGuid is None:
                    self._roleArcGuid = get_uid('_roleArcGuid')
                    entityType['roles'].append(
                        {
                        'allowsMultipleForEntity': True,
                        'allowsMultipleForEvent': True,
                        'allowsPercentAllocated': False,
                        'guid': self._roleArcGuid,
                        'icon': 'circle text',
                        'mandatoryForEntity': False,
                        'mandatoryForEvent': False,
                        'name': 'Arc',
                        'sortOrder': 0
                        })
                if self._roleStorylineGuid is None:
                    self._roleStorylineGuid = get_uid('_roleStorylineGuid')
                    entityType['roles'].append(
                        {
                        'allowsMultipleForEntity': True,
                        'allowsMultipleForEvent': True,
                        'allowsPercentAllocated': False,
                        'guid': self._roleStorylineGuid,
                        'icon': 'circle filled text',
                        'mandatoryForEntity': False,
                        'mandatoryForEvent': False,
                        'name': 'Storyline',
                        'sortOrder': 0
                        })

        #--- Add "Character" type, if missing.
        if self._typeCharacterGuid is None:
            self._typeCharacterGuid = get_uid('_typeCharacterGuid')
            self._roleCharacterGuid = get_uid('_roleCharacterGuid')
            typeCount = len(self._jsonData['template']['types'])
            self._jsonData['template']['types'].append(
                {
                    'color': 'iconRed',
                    'guid': self._typeCharacterGuid,
                    'icon': 'person',
                    'name': self._typeCharacter,
                    'persistent': False,
                    'roles': [
                        {
                            'allowsMultipleForEntity': True,
                            'allowsMultipleForEvent': True,
                            'allowsPercentAllocated': False,
                            'guid': self._roleCharacterGuid,
                            'icon': 'circle text',
                            'mandatoryForEntity': False,
                            'mandatoryForEvent': False,
                            'name': self._roleCharacter,
                            'sortOrder': 0
                        }
                    ],
                    'sortOrder': typeCount
                })

        #--- Add "Location" type, if missing.
        if self._typeLocationGuid is None:
            self._typeLocationGuid = get_uid('_typeLocationGuid')
            self._roleLocationGuid = get_uid('_roleLocationGuid')
            typeCount = len(self._jsonData['template']['types'])
            self._jsonData['template']['types'].append(
                {
                    'color': 'iconOrange',
                    'guid': self._typeLocationGuid,
                    'icon': 'map',
                    'name': self._typeLocation,
                    'persistent': True,
                    'roles': [
                        {
                            'allowsMultipleForEntity': True,
                            'allowsMultipleForEvent': True,
                            'allowsPercentAllocated': False,
                            'guid': self._roleLocationGuid,
                            'icon': 'circle text',
                            'mandatoryForEntity': False,
                            'mandatoryForEvent': False,
                            'name': self._roleLocation,
                            'sortOrder': 0
                        }
                    ],
                    'sortOrder': typeCount
                })

        #--- Add "Item" type, if missing.
        if self._typeItemGuid is None:
            self._typeItemGuid = get_uid('_typeItemGuid')
            self._roleItemGuid = get_uid('_roleItemGuid')
            typeCount = len(self._jsonData['template']['types'])
            self._jsonData['template']['types'].append(
                {
                    'color': 'iconPurple',
                    'guid': self._typeItemGuid,
                    'icon': 'cube',
                    'name': self._typeItem,
                    'persistent': True,
                    'roles': [
                        {
                            'allowsMultipleForEntity': True,
                            'allowsMultipleForEvent': True,
                            'allowsPercentAllocated': False,
                            'guid': self._roleItemGuid,
                            'icon': 'circle text',
                            'mandatoryForEntity': False,
                            'mandatoryForEvent': False,
                            'name': self._roleItem,
                            'sortOrder': 0
                        }
                    ],
                    'sortOrder': typeCount
                })

        #--- Get arcs, characters, locations, and items.
        # At the beginning, self.novel contains the  target data (if syncronizing an existing project),
        # or a newly instantiated Novel object (if creating a project).
        # This means, there may be already elements with IDs.
        # In order to reuse them, they are collected in the "target element ID by title" dictionaries.

        targetScIdByTitle = {}
        for scId in self.novel.scenes:
            title = self.novel.scenes[scId].title
            if title:
                if title in targetScIdByTitle:
                    raise Error(_('Ambiguous novelyst scene title "{}".').format(title))

                targetScIdByTitle[title] = scId

        targetCrIdByTitle = {}
        for crId in self.novel.characters:
            title = self.novel.characters[crId].title
            if title:
                if title in targetCrIdByTitle:
                    raise Error(_('Ambiguous novelyst character "{}".').format(title))

                targetCrIdByTitle[title] = crId

        targetLcIdByTitle = {}
        for lcId in self.novel.locations:
            title = self.novel.locations[lcId].title
            if title:
                if title in targetLcIdByTitle:
                    raise Error(_('Ambiguous novelyst location "{}".').format(title))

                targetLcIdByTitle[title] = lcId

        targetItIdByTitle = {}
        for itId in self.novel.items:
            title = self.novel.items[itId].title
            if title:
                if title in targetItIdByTitle:
                    raise Error(_('Ambiguous novelyst item "{}".').format(title))

                targetItIdByTitle[title] = itId

        # For scene relationship lookup:
        crIdsByGuid = {}
        lcIdsByGuid = {}
        itIdsByGuid = {}

        # For ambiguity check:
        characterNames = []
        locationNames = []
        itemNames = []

        for ent in self._jsonData['entities']:
            if ent['entityType'] == self._typeArcGuid:
                self._arcCount += 1
                if ent['name'] == self._entityNarrative:
                    self._entityNarrativeGuid = ent['guid']
                else:
                    self._arcGuidsByName[ent['name']] = ent['guid']

            elif ent['entityType'] == self._typeCharacterGuid:
                if ent['name'] in characterNames:
                    raise Error(_('Ambiguous Aeon character "{}".').format(ent['name']))

                characterNames.append(ent['name'])
                if ent['name'] in targetCrIdByTitle:
                    crId = targetCrIdByTitle[ent['name']]
                else:
                    crId = create_id(self.novel.characters)
                    self.novel.characters[crId] = Character()
                    self.novel.characters[crId].title = ent['name']
                    self.novel.srtCharacters.append(crId)
                crIdsByGuid[ent['guid']] = crId
                self._characterGuidById[crId] = ent['guid']
                if ent['notes']:
                    self.novel.characters[crId].notes = ent['notes']
                else:
                    ent['notes'] = ''

            elif ent['entityType'] == self._typeLocationGuid:
                if ent['name'] in locationNames:
                    raise Error(_('Ambiguous Aeon location "{}".').format(ent['name']))

                locationNames.append(ent['name'])
                if ent['name'] in targetLcIdByTitle:
                    lcId = targetLcIdByTitle[ent['name']]
                else:
                    lcId = create_id(self.novel.locations)
                    self.novel.locations[lcId] = WorldElement()
                    self.novel.locations[lcId].title = ent['name']
                    self.novel.srtLocations.append(lcId)
                lcIdsByGuid[ent['guid']] = lcId
                self._locationGuidById[lcId] = ent['guid']

            elif ent['entityType'] == self._typeItemGuid:
                if ent['name'] in itemNames:
                    raise Error(_('Ambiguous Aeon item "{}".').format(ent['name']))

                itemNames.append(ent['name'])
                if ent['name'] in targetItIdByTitle:
                    itId = targetItIdByTitle[ent['name']]
                else:
                    itId = create_id(self.novel.items)
                    self.novel.items[itId] = WorldElement()
                    self.novel.items[itId].title = ent['name']
                    self.novel.srtItems.append(itId)
                itIdsByGuid[ent['guid']] = itId
                self._itemGuidById[itId] = ent['guid']

        #--- Get GUID of user defined properties.
        hasPropertyNotes = False
        hasPropertyDesc = False
        for tplPrp in self._jsonData['template']['properties']:
            if tplPrp['name'] == self._propertyDesc:
                self._propertyDescGuid = tplPrp['guid']
                hasPropertyDesc = True
            elif tplPrp['name'] == self._propertyNotes:
                self._propertyNotesGuid = tplPrp['guid']
                hasPropertyNotes = True
            elif tplPrp['name'] == self.PROPERTY_MOONPHASE:
                self._propertyMoonphaseGuid = tplPrp['guid']

        #--- Create user defined properties, if missing.
        if not hasPropertyNotes:
            for tplPrp in self._jsonData['template']['properties']:
                tplPrp['sortOrder'] += 1
            self._propertyNotesGuid = get_uid('_propertyNotesGuid')
            self._jsonData['template']['properties'].insert(0, {
                'calcMode': 'default',
                'calculate': False,
                'fadeEvents': False,
                'guid': self._propertyNotesGuid,
                'icon': 'tag',
                'isMandatory': False,
                'name': self._propertyNotes,
                'sortOrder': 0,
                'type': 'multitext'
            })
        if not hasPropertyDesc:
            n = len(self._jsonData['template']['properties'])
            self._propertyDescGuid = get_uid('_propertyDescGuid')
            self._jsonData['template']['properties'].append({
                'calcMode': 'default',
                'calculate': False,
                'fadeEvents': False,
                'guid': self._propertyDescGuid,
                'icon': 'tag',
                'isMandatory': False,
                'name': self._propertyDesc,
                'sortOrder': n,
                'type': 'multitext'
            })
        if self._addMoonphase and self._propertyMoonphaseGuid is None:
            n = len(self._jsonData['template']['properties'])
            self._propertyMoonphaseGuid = get_uid('_propertyMoonphaseGuid')
            self._jsonData['template']['properties'].append({
                'calcMode': 'default',
                'calculate': False,
                'fadeEvents': False,
                'guid': self._propertyMoonphaseGuid,
                'icon': 'flag',
                'isMandatory': False,
                'name': self.PROPERTY_MOONPHASE,
                'sortOrder': n,
                'type': 'text'
            })

        #--- Update/create scenes.
        scIdsByDate = {}
        scnTitles = []
        narrativeEvents = []
        for evt in self._jsonData['events']:

            # Find out whether the event is associated to a normal scene:
            isNarrative = False
            for evtRel in evt['relationships']:
                if evtRel['role'] == self._roleArcGuid:
                    if self._entityNarrativeGuid and evtRel['entity'] == self._entityNarrativeGuid:
                        isNarrative = True

            if evt['title'] in scnTitles:
                raise Error(f'Ambiguous Aeon event title "{evt["title"]}".')

            evt['title'] = evt['title'].strip()
            scnTitles.append(evt['title'])
            if evt['title'] in targetScIdByTitle:
                scId = targetScIdByTitle[evt['title']]
            else:
                if self._scenesOnly and not isNarrative:
                    # don't create a "Notes" scene
                    continue

                # Create a new scene.
                scId = create_id(self.novel.scenes)
                self.novel.scenes[scId] = Scene()
                self.novel.scenes[scId].title = evt['title']
                # print(f'read creates {self.novel.scenes[scId].title}')
                self.novel.scenes[scId].status = 1
                self.novel.scenes[scId].scType = 0
                self.novel.scenes[scId].scPacing = 0

            narrativeEvents.append(scId)
            displayId = float(evt['displayId'])
            if displayId > self._displayIdMax:
                self._displayIdMax = displayId

            #--- Evaluate properties.
            hasDescription = False
            hasNotes = False
            for evtVal in evt['values']:

                # Get scene description.
                if evtVal['property'] == self._propertyDescGuid:
                    hasDescription = True
                    if evtVal['value']:
                        self.novel.scenes[scId].desc = evtVal['value']

                # Get scene notes.
                elif evtVal['property'] == self._propertyNotesGuid:
                    hasNotes = True
                    if evtVal['value']:
                        self.novel.scenes[scId].notes = evtVal['value']

            #--- Add description and scene notes, if missing.
            if not hasDescription:
                evt['values'].append({'property': self._propertyDescGuid, 'value': ''})
            if not hasNotes:
                evt['values'].append({'property': self._propertyNotesGuid, 'value': ''})

            #--- Get scene tags.
            if evt['tags']:
                self.novel.scenes[scId].tags = []
                for evtTag in evt['tags']:
                    self.novel.scenes[scId].tags.append(evtTag)

            #--- Get date/time/duration
            timestamp = 0
            for evtRgv in evt['rangeValues']:
                if evtRgv['rangeProperty'] == self._tplDateGuid:
                    timestamp = evtRgv['position']['timestamp']
                    if timestamp >= self.DATE_LIMIT:
                        # Restrict date/time calculation to dates within novelyst's range
                        sceneStart = datetime.min + timedelta(seconds=timestamp)
                        startDateTime = sceneStart.isoformat().split('T')

                        # Has the source an unspecific date?
                        if self.novel.scenes[scId].day is not None:
                            # Convert date to day.
                            sceneDelta = sceneStart - self.referenceDate
                            self.novel.scenes[scId].day = str(sceneDelta.days)
                        elif (self.novel.scenes[scId].time is not None) and (self.novel.scenes[scId].date is None):
                            # Use the default date.
                            self.novel.scenes[scId].day = '0'
                        else:
                            self.novel.scenes[scId].date = startDateTime[0]
                        self.novel.scenes[scId].time = startDateTime[1]

                        # Calculate duration
                        if 'years' in evtRgv['span'] or 'months' in evtRgv['span']:
                            endYear = sceneStart.year
                            endMonth = sceneStart.month
                            if 'years' in evtRgv['span']:
                                endYear += evtRgv['span']['years']
                            if 'months' in evtRgv['span']:
                                endMonth += evtRgv['span']['months']
                                while endMonth > 12:
                                    endMonth -= 12
                                    endYear += 1
                            sceneEnd = datetime(endYear, endMonth, sceneStart.day)
                            sceneDuration = sceneEnd - datetime(sceneStart.year, sceneStart.month, sceneStart.day)
                            lastsDays = sceneDuration.days
                            lastsHours = sceneDuration.seconds // 3600
                            lastsMinutes = (sceneDuration.seconds % 3600) // 60
                        else:
                            lastsDays = 0
                            lastsHours = 0
                            lastsMinutes = 0
                        if 'weeks' in evtRgv['span']:
                            lastsDays += evtRgv['span']['weeks'] * 7
                        if 'days' in evtRgv['span']:
                            lastsDays += evtRgv['span']['days']
                        if 'hours' in evtRgv['span']:
                            lastsDays += evtRgv['span']['hours'] // 24
                            lastsHours += evtRgv['span']['hours'] % 24
                        if 'minutes' in evtRgv['span']:
                            lastsHours += evtRgv['span']['minutes'] // 60
                            lastsMinutes += evtRgv['span']['minutes'] % 60
                        if 'seconds' in evtRgv['span']:
                            lastsMinutes += evtRgv['span']['seconds'] // 60
                        lastsHours += lastsMinutes // 60
                        lastsMinutes %= 60
                        lastsDays += lastsHours // 24
                        lastsHours %= 24
                        self.novel.scenes[scId].lastsDays = str(lastsDays)
                        self.novel.scenes[scId].lastsHours = str(lastsHours)
                        self.novel.scenes[scId].lastsMinutes = str(lastsMinutes)
                    break

            # Use the timestamp for chronological sorting.
            if not timestamp in scIdsByDate:
                scIdsByDate[timestamp] = []
            scIdsByDate[timestamp].append(scId)

            #--- Find scenes and get characters, locations, and items.
            self.novel.scenes[scId].scType = 1
            # type = "Notes"
            self.novel.scenes[scId].characters = None
            self.novel.scenes[scId].locations = None
            self.novel.scenes[scId].items = None
            arcs = []
            for evtRel in evt['relationships']:
                if evtRel['role'] == self._roleArcGuid:
                    # Make scene event "Normal" type scene.
                    if self._entityNarrativeGuid and evtRel['entity'] == self._entityNarrativeGuid:
                        self.novel.scenes[scId].scType = 0
                        # type = "Normal"
                        if timestamp > self._timestampMax:
                            self._timestampMax = timestamp
                if evtRel['role'] == self._roleStorylineGuid:
                    # Collect scene arcs.
                    for arcName in self._arcGuidsByName:
                        if evtRel['entity'] == self._arcGuidsByName[arcName]:
                            arcs.append(arcName)
                elif evtRel['role'] == self._roleCharacterGuid:
                    if self.novel.scenes[scId].characters is None:
                        self.novel.scenes[scId].characters = []
                    crId = crIdsByGuid[evtRel['entity']]
                    self.novel.scenes[scId].characters.append(crId)
                elif evtRel['role'] == self._roleLocationGuid:
                    if self.novel.scenes[scId].locations is None:
                        self.novel.scenes[scId].locations = []
                    lcId = lcIdsByGuid[evtRel['entity']]
                    self.novel.scenes[scId].locations.append(lcId)
                elif evtRel['role'] == self._roleItemGuid:
                    if self.novel.scenes[scId].items is None:
                        self.novel.scenes[scId].items = []
                    itId = itIdsByGuid[evtRel['entity']]
                    self.novel.scenes[scId].items.append(itId)

            # Add arcs to the scene keyword variables.
            self.novel.scenes[scId].arcs = list_to_string(arcs)

        #--- Mark scenes deleted in Aeon "Unused".
        for scId in self.novel.scenes:
            if not scId in narrativeEvents:
                if self.novel.scenes[scId].scType == 0:
                    self.novel.scenes[scId].scType = 3

        #--- Make sure every scene is assigned to a chapter.
        scenesInChapters = []
        # List all scenes already assigned to a chapter.
        for chId in self.novel.tree.get_children(CH_ROOT):
            scenesInChapters.extend(self.novel.tree.get_children(chId))

        # Create a chapter for new scenes.
        newChapterId = create_id(self.novel.srtChapters)
        newChapter = Chapter()
        newChapter.title = _('New scenes')
        newChapter.chType = 0

        # Sort scenes by date/time, then put the orphaned ones into the new chapter.
        srtScenes = sorted(scIdsByDate.items())
        for __, scList in srtScenes:
            for scId in scList:
                if not scId in scenesInChapters:
                    if not newChapterId in self.novel.srtChapters:
                        self.novel.chapters[newChapterId] = newChapter
                        self.novel.srtChapters.append(newChapterId)
                    self.novel.chapters[newChapterId].srtScenes.append(scId)

        if self._timestampMax == 0:
            self._timestampMax = (self.referenceDate - datetime.min).total_seconds()

    def write(self):
        """Write instance variables to the file.
        
        Update instance variables from a source instance.              
        Update date/time/duration from the source,
        if the scene title matches.
        Overrides the superclass method.
        """

        def get_timestamp(scene):
            """Return a timestamp integer from the scene date.
            
            Positional arguments:
                scene -- Scene instance
            """
            self._timestampMax += 1
            timestamp = int(self._timestampMax)
            try:
                if scene.date:
                    isoDt = scene.date
                    if scene.time:
                        isoDt = (f'{isoDt} {scene.time}')
                timestamp = int((datetime.fromisoformat(isoDt) - datetime.min).total_seconds())
            except:
                pass
            return timestamp

        def get_span(scene):
            """Return a time span dictionary from the scene duration.
            
            Positional arguments:
                scene -- Scene instance
            """
            span = {}
            if scene.lastsDays:
                span['days'] = int(scene.lastsDays)
            if scene.lastsHours:
                span['hours'] = int(scene.lastsHours)
            if scene.lastsMinutes:
                span['minutes'] = int(scene.lastsMinutes)
            return span

        def get_display_id():
            self._displayIdMax += 1
            return str(int(self._displayIdMax))

        def build_event(scene):
            """Create a new event from a scene.
            """
            event = {
                'attachments': [],
                'color': '',
                'displayId': get_display_id(),
                'guid': get_uid(f'scene{scene.title}'),
                'links': [],
                'locked': False,
                'priority': 500,
                'rangeValues': [{
                    'minimumZoom':-1,
                    'position': {
                        'precision': 'minute',
                        'timestamp': self.DATE_LIMIT
                    },
                    'rangeProperty': self._tplDateGuid,
                    'span': {},
                }],
                'relationships': [],
                'tags': [],
                'title': scene.title,
                'values': [{
                    'property': self._propertyNotesGuid,
                    'value': ''
                },
                    {
                    'property': self._propertyDescGuid,
                    'value': ''
                }],
            }
            if scene.scType == 1:
                event['color'] = self._colors[self._eventColor]
            elif scene.scType == 2:
                event['color'] = self._colors[self._pointColor]
            else:
                event['color'] = self._colors[self._sceneColor]
            return event

        #--- Merge first.
        source = self.novel
        self.novel = Novel()
        self.read()
        # create a new target novel from the aeon2 project file

        targetEvents = []
        for evt in self._jsonData['events']:
            targetEvents.append(evt['title'])

        linkedCharacters = []
        linkedLocations = []
        linkedItems = []

        #--- Check the source for ambiguous titles.
        # Check scenes.
        srcScnTitles = []
        for chId in source.chapters:
            if source.chapters[chId].isTrash:
                continue

            for scId in source.get_tree_elements(chId):
                if source.scenes[scId].title in srcScnTitles:
                    raise Error(_('Ambiguous novelyst scene title "{}".').format(source.scenes[scId].title))

                srcScnTitles.append(source.scenes[scId].title)

                #--- Collect characters, locations, and items assigned to scenes.
                if source.scenes[scId].characters:
                    linkedCharacters = list(set(linkedCharacters + source.scenes[scId].characters))
                if source.scenes[scId].locations:
                    linkedLocations = list(set(linkedLocations + source.scenes[scId].locations))
                if source.scenes[scId].items:
                    linkedItems = list(set(linkedItems + source.scenes[scId].items))

                #--- Collect arcs from source.
                arcs = string_to_list(source.scenes[scId].arcs)
                for arc in arcs:
                    if not arc in self._arcGuidsByName:
                        self._arcGuidsByName[arc] = None
                        # new arc; GUID is generated on writing

        # Check characters.
        srcChrNames = []
        for crId in source.characters:
            if not crId in linkedCharacters:
                continue

            if source.characters[crId].title in srcChrNames:
                raise Error(_('Ambiguous novelyst character "{}".').format(source.characters[crId].title))

            srcChrNames.append(source.characters[crId].title)

        # Check locations.
        srcLocTitles = []
        for lcId in source.locations:
            if not lcId in linkedLocations:
                continue

            if source.locations[lcId].title in srcLocTitles:
                raise Error(_('Ambiguous novelyst location "{}".').format(source.locations[lcId].title))

            srcLocTitles.append(source.locations[lcId].title)

        # Check items.
        srcItmTitles = []
        for itId in source.items:
            if not itId in linkedItems:
                continue

            if source.items[itId].title in srcItmTitles:
                raise Error(_('Ambiguous novelyst item "{}".').format(source.items[itId].title))

            srcItmTitles.append(source.items[itId].title)

        #--- Check the target for ambiguous titles.
        # Check scenes.
        scIdsByTitle = {}
        for scId in self.novel.scenes:
            if self.novel.scenes[scId].title in scIdsByTitle:
                raise Error(_('Ambiguous Aeon event title "{}".').format(self.novel.scenes[scId].title))

            scIdsByTitle[self.novel.scenes[scId].title] = scId
            # print(f'merge finds {self.novel.scenes[scId].title}')

            #--- Mark non-scene events.
            # This is to recognize "Trash" scenes.
            if not self.novel.scenes[scId].title in srcScnTitles:
                if not self.novel.scenes[scId].scType == 1:
                    self._trashEvents.append(scId)

        # Check characters.
        crIdsByTitle = {}
        for crId in self.novel.characters:
            if self.novel.characters[crId].title in crIdsByTitle:
                raise Error(_('Ambiguous Aeon character "{}".').format(self.novel.characters[crId].title))

            crIdsByTitle[self.novel.characters[crId].title] = crId

        # Check locations.
        lcIdsByTitle = {}
        for lcId in self.novel.locations:
            if self.novel.locations[lcId].title in lcIdsByTitle:
                raise Error(_('Ambiguous Aeon location "{}".').format(self.novel.locations[lcId].title))

            lcIdsByTitle[self.novel.locations[lcId].title] = lcId

        # Check items.
        itIdsByTitle = {}
        for itId in self.novel.items:
            if self.novel.items[itId].title in itIdsByTitle:
                raise Error(_('Ambiguous Aeon item "{}".').format(self.novel.items[itId].title))

            itIdsByTitle[self.novel.items[itId].title] = itId

        #--- Update characters from the source.
        crIdMax = len(self.novel.characters)
        crIdsBySrcId = {}
        for srcCrId in source.characters:
            if source.characters[srcCrId].title in crIdsByTitle:
                crIdsBySrcId[srcCrId] = crIdsByTitle[source.characters[srcCrId].title]
            elif srcCrId in linkedCharacters:
                #--- Create a new character if it is assigned to at least one scene.
                crIdMax += 1
                crId = str(crIdMax)
                crIdsBySrcId[srcCrId] = crId
                self.novel.characters[crId] = source.characters[srcCrId]
                newGuid = get_uid(f'{crId}{self.novel.characters[crId].title}')
                self._characterGuidById[crId] = newGuid
                self._jsonData['entities'].append(
                    {
                        'entityType': self._typeCharacterGuid,
                        'guid': newGuid,
                        'icon': 'person',
                        'name': self.novel.characters[crId].title,
                        'notes': '',
                        'sortOrder': crIdMax - 1,
                        'swatchColor': 'darkPink'
                    })

        #--- Update locations from the source.
        lcIdMax = len(self.novel.locations)
        lcIdsBySrcId = {}
        for srcLcId in source.locations:
            if source.locations[srcLcId].title in lcIdsByTitle:
                lcIdsBySrcId[srcLcId] = lcIdsByTitle[source.locations[srcLcId].title]
            elif srcLcId in linkedLocations:
                #--- Create a new location if it is assigned to at least one scene.
                lcIdMax += 1
                lcId = str(lcIdMax)
                lcIdsBySrcId[srcLcId] = lcId
                self.novel.locations[lcId] = source.locations[srcLcId]
                newGuid = get_uid(f'{lcId}{self.novel.locations[lcId].title}')
                self._locationGuidById[lcId] = newGuid
                self._jsonData['entities'].append(
                    {
                        'entityType': self._typeLocationGuid,
                        'guid': newGuid,
                        'icon': 'map',
                        'name': self.novel.locations[lcId].title,
                        'notes': '',
                        'sortOrder': lcIdMax - 1,
                        'swatchColor': 'orange'
                    })

        #--- Update Items from the source.
        itIdMax = len(self.novel.items)
        itIdsBySrcId = {}
        for srcItId in source.items:
            if source.items[srcItId].title in itIdsByTitle:
                itIdsBySrcId[srcItId] = itIdsByTitle[source.items[srcItId].title]
            elif srcItId in linkedItems:
                #--- Create a new Item if it is assigned to at least one scene.
                itIdMax += 1
                itId = str(itIdMax)
                itIdsBySrcId[srcItId] = itId
                self.novel.items[itId] = source.items[srcItId]
                newGuid = get_uid(f'{itId}{self.novel.items[itId].title}')
                self._itemGuidById[itId] = newGuid
                self._jsonData['entities'].append(
                    {
                        'entityType': self._typeItemGuid,
                        'guid': newGuid,
                        'icon': 'cube',
                        'name': self.novel.items[itId].title,
                        'notes': '',
                        'sortOrder': itIdMax - 1,
                        'swatchColor': 'denim'
                    })

        #--- Update scenes from the source.
        totalEvents = len(self._jsonData['events'])
        for chId in source.chapters:
            for srcId in source.get_tree_elements(chId):
                if source.scenes[srcId].scType == 3:
                    # Remove unused scene from the "Narrative" arc.
                    if source.scenes[srcId].title in scIdsByTitle:
                        scId = scIdsByTitle[source.scenes[srcId].title]
                        self.novel.scenes[scId].scType = 1
                    continue

                if source.scenes[srcId].scType == 1 and self._scenesOnly:
                    # Remove unsynchronized scene from the "Narrative" arc.
                    if source.scenes[srcId].title in scIdsByTitle:
                        scId = scIdsByTitle[source.scenes[srcId].title]
                        self.novel.scenes[scId].scType = 1
                    continue

                if source.scenes[srcId].scType == 2 and source.scenes[srcId].arcs is None:
                    # Remove "non-point" Todo scene from the "Narrative" arc.
                    if source.scenes[srcId].title in scIdsByTitle:
                        scId = scIdsByTitle[source.scenes[srcId].title]
                        self.novel.scenes[scId].scType = 1
                    continue

                if source.scenes[srcId].title in scIdsByTitle:
                    scId = scIdsByTitle[source.scenes[srcId].title]
                elif source.scenes[srcId].title in targetEvents:
                    # catch non-narrative events in the target
                    continue

                else:
                    #--- Create a new scene.
                    totalEvents += 1
                    scId = str(totalEvents)
                    self.novel.scenes[scId] = Scene()
                    self.novel.scenes[scId].title = source.scenes[srcId].title
                    # print(f'merge creates {self.novel.scenes[scId].title}')
                    scIdsByTitle[self.novel.scenes[scId].title] = scId
                    self.novel.scenes[scId].scType = source.scenes[srcId].scType
                    self.novel.scenes[scId].scPacing = source.scenes[srcId].scPacing
                    newEvent = build_event(self.novel.scenes[scId])
                    self._jsonData['events'].append(newEvent)
                self.novel.scenes[scId].status = source.scenes[srcId].status

                #--- Update scene type.
                if source.scenes[srcId].scType is not None:
                    self.novel.scenes[scId].scType = source.scenes[srcId].scType

                #--- Update scene tags.
                if source.scenes[srcId].tags is not None:
                    self.novel.scenes[scId].tags = source.scenes[srcId].tags

                #--- Update scene description.
                if source.scenes[srcId].desc is not None:
                    self.novel.scenes[scId].desc = source.scenes[srcId].desc

                #--- Update scene characters.
                if source.scenes[srcId].characters is not None:
                    self.novel.scenes[scId].characters = []
                    for crId in source.scenes[srcId].characters:
                        if crId in crIdsBySrcId:
                            self.novel.scenes[scId].characters.append(crIdsBySrcId[crId])

                #--- Update scene locations.
                if source.scenes[srcId].locations is not None:
                    self.novel.scenes[scId].locations = []
                    for lcId in source.scenes[srcId].locations:
                        if lcId in lcIdsBySrcId:
                            self.novel.scenes[scId].locations.append(lcIdsBySrcId[lcId])

                #--- Update scene items.
                if source.scenes[srcId].items is not None:
                    self.novel.scenes[scId].items = []
                    for itId in source.scenes[srcId].items:
                        if itId in itIdsBySrcId:
                            self.novel.scenes[scId].items.append(itIdsBySrcId[itId])

                #--- Update scene arcs.
                self.novel.scenes[scId].arcs = source.scenes[srcId].arcs

                #--- Update scene start date/time.
                if source.scenes[srcId].time is not None:
                    self.novel.scenes[scId].time = source.scenes[srcId].time

                #--- Calculate event date from unspecific scene date, if any:
                if source.scenes[srcId].day is not None:
                    dayInt = int(source.scenes[srcId].day)
                    sceneDelta = timedelta(days=dayInt)
                    self.novel.scenes[scId].date = (self.referenceDate + sceneDelta).isoformat().split('T')[0]
                elif (source.scenes[srcId].date is None) and (source.scenes[srcId].time is not None):
                    self.novel.scenes[scId].date = self.referenceDate.isoformat().split('T')[0]
                else:
                    self.novel.scenes[scId].date = source.scenes[srcId].date

                #--- Update scene duration.
                if source.scenes[srcId].lastsMinutes is not None:
                    self.novel.scenes[scId].lastsMinutes = source.scenes[srcId].lastsMinutes
                if source.scenes[srcId].lastsHours is not None:
                    self.novel.scenes[scId].lastsHours = source.scenes[srcId].lastsHours
                if source.scenes[srcId].lastsDays is not None:
                    self.novel.scenes[scId].lastsDays = source.scenes[srcId].lastsDays

        #--- Begin writing

        #--- Add "Narrative" arc, if missing.
        if self._entityNarrativeGuid is None:
            self._entityNarrativeGuid = get_uid('entityNarrativeGuid')
            self._jsonData['entities'].append(
                {
                    'entityType': self._typeArcGuid,
                    'guid': self._entityNarrativeGuid,
                    'icon': 'book',
                    'name': self._entityNarrative,
                    'notes': '',
                    'sortOrder': self._arcCount,
                    'swatchColor': 'orange'
                })
            self._arcCount += 1
        narrativeArc = {
            'entity': self._entityNarrativeGuid,
            'percentAllocated': 1,
            'role': self._roleArcGuid,
        }

        #--- Add missing arcs.
        arcs = {}
        for arcName in self._arcGuidsByName:
            if self._arcGuidsByName[arcName] is None:
                guid = get_uid(f'entity{arcName}ArcGuid')
                self._arcGuidsByName[arcName] = guid
                self._jsonData['entities'].append(
                    {
                        'entityType': self._typeArcGuid,
                        'guid': guid,
                        'icon': 'book',
                        'name': arcName,
                        'notes': '',
                        'sortOrder': self._arcCount,
                        'swatchColor': 'orange'
                    })
                self._arcCount += 1
            arcs[arcName] = {
                'entity': self._arcGuidsByName[arcName],
                'percentAllocated': 1,
                'role': self._roleStorylineGuid,
            }

        #--- Update events from scenes.
        for evt in self._jsonData['events']:
            try:
                scId = scIdsByTitle[evt['title']]
            except KeyError:
                continue

            #--- Set event date/time/span.
            if evt['rangeValues'][0]['position']['timestamp'] >= self.DATE_LIMIT:
                evt['rangeValues'][0]['span'] = get_span(self.novel.scenes[scId])
                evt['rangeValues'][0]['position']['timestamp'] = get_timestamp(self.novel.scenes[scId])

            #--- Calculate moon phase.
            if self._propertyMoonphaseGuid is not None:
                eventMoonphase = get_moon_phase_plus(self.novel.scenes[scId].date)
            else:
                eventMoonphase = ''

            #--- Set scene description, notes, and moon phase.
            hasMoonphase = False
            for evtVal in evt['values']:

                # Set scene description.
                if evtVal['property'] == self._propertyDescGuid:
                    if self.novel.scenes[scId].desc:
                        evtVal['value'] = self.novel.scenes[scId].desc

                # Set scene notes.
                elif evtVal['property'] == self._propertyNotesGuid:
                    if self.novel.scenes[scId].notes:
                        evtVal['value'] = self.novel.scenes[scId].notes

                # Set moon phase.
                elif evtVal['property'] == self._propertyMoonphaseGuid:
                        evtVal['value'] = eventMoonphase
                        hasMoonphase = True

            #--- Add missing event properties.
            if not hasMoonphase and self._propertyMoonphaseGuid is not None:
                evt['values'].append({'property': self._propertyMoonphaseGuid, 'value': eventMoonphase})

            #--- Set scene tags.
            if self.novel.scenes[scId].tags:
                evt['tags'] = self.novel.scenes[scId].tags

            #--- Update characters, locations, and items.
            # Delete assignments.
            newRel = []
            for evtRel in evt['relationships']:
                if evtRel['role'] == self._roleCharacterGuid:
                    continue

                elif evtRel['role'] == self._roleLocationGuid:
                    continue

                elif evtRel['role'] == self._roleItemGuid:
                    continue

                else:
                    newRel.append(evtRel)

            # Add characters.
            if self.novel.scenes[scId].characters:
                for crId in self.novel.scenes[scId].characters:
                    newRel.append(
                        {
                            'entity': self._characterGuidById[crId],
                            'percentAllocated': 1,
                            'role': self._roleCharacterGuid,
                        })

            # Add locations.
            if self.novel.scenes[scId].locations:
                for lcId in self.novel.scenes[scId].locations:
                    newRel.append(
                        {
                            'entity': self._locationGuidById[lcId],
                            'percentAllocated': 1,
                            'role': self._roleLocationGuid,
                        })

            # Add items.
            if self.novel.scenes[scId].items:
                for itId in self.novel.scenes[scId].items:
                    newRel.append(
                        {
                            'entity': self._itemGuidById[itId],
                            'percentAllocated': 1,
                            'role': self._roleItemGuid,
                        })

            evt['relationships'] = newRel

            #--- Assign "scene" events to the "Narrative" arc.
            if self.novel.scenes[scId].scType == 0:
                if narrativeArc not in evt['relationships']:
                    evt['relationships'].append(narrativeArc)

                #--- Assign events to arcs.
                sceneArcs = string_to_list(self.novel.scenes[scId].arcs)
                for arcName in arcs:
                    if arcName in sceneArcs:
                        if arcs[arcName] not in evt['relationships']:
                            evt['relationships'].append(arcs[arcName])
                    else:
                        try:
                            evt['relationships'].remove(arcs[arcName])
                        except:
                            pass

            elif self.novel.scenes[scId].scType == 2:
                if narrativeArc in evt['relationships']:
                    evt['relationships'].remove(narrativeArc)

                #--- Assign events to arcs.
                sceneArcs = string_to_list(self.novel.scenes[scId].arcs)
                for arcName in arcs:
                    if arcName in sceneArcs:
                        if arcs[arcName] not in evt['relationships']:
                            evt['relationships'].append(arcs[arcName])
                    else:
                        try:
                            evt['relationships'].remove(arcs[arcName])
                        except:
                            pass

            elif self.novel.scenes[scId].scType == 1:
                if narrativeArc in evt['relationships']:
                    evt['relationships'].remove(narrativeArc)

                #--- Clear arcs, if any.
                sceneArcs = string_to_list(self.novel.scenes[scId].arcs)
                for arcName in sceneArcs:
                    evt['relationships'].remove(arcs[arcName])

        #--- Delete "Trash" scenes.
        events = []
        for evt in self._jsonData['events']:
            try:
                scId = scIdsByTitle[evt['title']]
            except KeyError:
                events.append(evt)
            else:
                if not scId in self._trashEvents:
                    events.append(evt)
        self._jsonData['events'] = events
        save_timeline(self._jsonData, self.filePath)
