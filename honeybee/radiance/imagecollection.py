"""Image collection class.

Image collection class is similar to AnalysisGrid but for image-based analysis.
Use ImageCollection to collect the path to different images and generate their
combinations using pcomb.
"""
from .command.pcomb import Pcomb, PcombImage
from collections import defaultdict, OrderedDict
import types
from itertools import izip
import os

import ladybug.dt as dt


# TODO(mostapha): This class needs to be reviewed and tested.
# It has been put together in the last minute before the release.
class ImageCollection(object):
    """Image collection.

    Image collection class is similar to AnalysisGrid but for image-based analysis.
    Use ImageCollection to collect the path to different images and generate their
    combinations using pcomb.
    """

    def __init__(self, name='untitled', outputFolder=None):
        """Initiate an image collection."""
        # name of sources and their state. It's only meaningful in multi-phase daylight
        # analysis. In analysis for a single time it will be {None: [None]}
        # It is set inside _createDataStructure method on setting values.
        self._sources = OrderedDict()

        # an empty list for values
        # for each source there will be a new list
        # inside each source list there will be a dictionary for each state
        # in each dictionary the key is the hoy and the values are a list which
        # is [total, direct]. If the value is not available it will be None
        self._values = []
        self.name = name or 'untitled'
        self.outputFolder = outputFolder or '.'

    @property
    def sources(self):
        """Get sorted list of light sources.

        In most of the cases light sources are window groups.
        """
        srcs = range(len(self._sources))
        for name, d in self._sources.iteritems():
            srcs[d['id']] = name
        return srcs

    @property
    def details(self):
        """Human readable details."""
        header = '#hours: {}\n#window groups: {}\n'.format(
            len(self.hoys), len(self._sources)
        )
        sep = '-' * 15
        wg = '\nWindow Group {}: {}\n'
        st = '....State {}: {}\n'

        # sort sources based on ids
        sources = range(len(self._sources))
        for s, d in self._sources.iteritems():
            sources[d['id']] = (s, d)

        # create the string for eacj window groups
        notes = [header, sep]
        for count, s in enumerate(sources):
            name, states = s
            notes.append(wg.format(count, name))
            for count, name in enumerate(states['state']):
                notes.append(st.format(count, name))

        return ''.join(notes)

    @property
    def hasValues(self):
        """Check if this point has results values."""
        return len(self._values) != 0

    @property
    def hoys(self):
        """Return hours of the year for results if any."""
        if not self.hasValues:
            return []
        else:
            return sorted(self._values[0][0].keys())

    def sourceId(self, source):
        """Get source id from source name."""
        # find the id for source and state
        try:
            return self._sources[source]['id']
        except KeyError:
            raise ValueError('Invalid source input: {}'.format(source))

    def blindStateId(self, source, state):
        """Get state id if available."""
        try:
            return int(state)
        except ValueError:
            pass

        try:
            return self._sources[source]['state'].index(state)
        except ValueError:
            raise ValueError('Invalid state input: {}'.format(state))

    def sourceStateName(self, sid, stateid):
        """Get source and state name based on ids."""
        sourceName = None
        for k, v in self._sources.iteritems():
            if v['id'] == sid:
                sourceName = k
                break
        assert sourceName, \
            ValueError('Failed to find source name for sid [{}]'.format(sid))

        # find state name
        try:
            return sourceName, self._sources[sourceName]['state'][stateid]
        except IndexError:
            raise IndexError(
                'State id [{}] is not valid. {} has {} states.'
                .format(stateid, sourceName, len(self._sources[sourceName]['state'])))

    @property
    def states(self):
        """Get list of states names for each source."""
        return tuple(s[1]['state'] for s in self._sources.iteritems())

    def _createDataStructure(self, source, state):
        """Create place holders for sources and states if needed.

        Returns:
            source id and state id as a tuple.
        """
        def triple():
            """Place holder for three files.

            Total, direct and sun hdr images file path. The final image is the result
            of total - direct + sun.
            """
            return [None, None, None]

        currentSources = self._sources.keys()
        if source not in currentSources:
            self._sources[source] = {
                'id': len(currentSources),
                'state': []
            }

            # append a new list to values for the new source
            self._values.append([])

        # find the id for source and state
        sid = self._sources[source]['id']

        if state not in self._sources[source]['state']:
            # add sources
            self._sources[source]['state'].append(state)
            # append a new dictionary for this state
            self._values[sid].append(defaultdict(triple))

        # find the state id
        stateid = self._sources[source]['state'].index(state)

        return sid, stateid

    def addImageFile(self, filePath, hoy, source=None, state=None, index=0):
        """Set value for a specific hour of the year.

        Args:
            value: Value as a number.
            hoy: The hour of the year that corresponds to this value.
            source: Name of the source of light. Only needed in case of multiple
                sources / window groups (default: None).
            state: State of the source if any (default: None).
            index: 0 > Default scene, 1 > Direct, 2 > Sun.
        """
        if hoy is None:
            return
        sid, stateid = self._createDataStructure(source, state)
        self._values[sid][stateid][hoy][index] = filePath

    def addImageFiles(self, filePaths, hoys, source=None, state=None, index=0):
        """Set values for several hours of the year.

        Args:
            filePaths: List of file paths as string.
            hoys: List of hours of the year that corresponds to input values.
            source: Name of the source of light. Only needed in case of multiple
                sources / window groups (default: None).
            state: State of the source if any (default: None).
            index: 0 > Default scene, 1 > Direct, 2 > Sun.
        """
        if not (isinstance(filePaths, types.GeneratorType) or
                isinstance(hoys, types.GeneratorType)):

            assert len(filePaths) == len(hoys), \
                ValueError(
                    'Length of values [%d] is not equal to length of hoys [%d].'
                    % (len(filePaths), len(hoys)))

        sid, stateid = self._createDataStructure(source, state)

        ind = index or 0

        for hoy, value in izip(hoys, filePaths):
            if hoy is None:
                continue
            try:
                self._values[sid][stateid][hoy][ind] = value
            except Exception as e:
                raise ValueError(
                    'Failed to load {} results for window_group [{}], state[{}]'
                    ' for hour {}.\n{}'.format('direct' if index else 'total',
                                               sid, stateid, hoy, e)
                )

    def addCoupledImageFiles(self, filePaths, hoys, source=None, state=None):
        """Set total, direct and sun file paths for several hours of the year.

        Args:
            filePaths: List of filepaths as tuples (total, direct, sun).
            hoys: List of hours of the year that corresponds to input values.
            source: Name of the source of light. Only needed in case of multiple
                sources / window groups (default: None).
            state: State of the source if any (default: None).
        """
        if not (isinstance(filePaths, types.GeneratorType) or
                isinstance(hoys, types.GeneratorType)):

            assert len(filePaths) == len(hoys), \
                ValueError(
                    'Length of values [%d] is not equal to length of hoys [%d].'
                    % (len(filePaths), len(hoys)))

        sid, stateid = self._createDataStructure(source, state)

        for hoy, filepathCol in izip(hoys, filePaths):
            if hoy is None:
                continue
            try:
                self._values[sid][stateid][hoy] = \
                    filepathCol[0], filepathCol[1], filepathCol[2]
            except TypeError:
                raise ValueError(
                    "Wrong input: {}. Input values must be of length of 3."
                    .format(filepathCol)
                )
            except IndexError:
                raise ValueError(
                    "Wrong input: {}. Input values must be of length of 3."
                    .format(filepathCol)
                )

    def getImage(self, hoy, source=None, state=None):
        """Get list of images for an hour in the year."""
        sid = self.sourceId(source)
        # find the state id
        stateid = self.blindStateId(source, state)

        if hoy not in self._values[sid][stateid]:
            raise ValueError('Hourly values are not available for {}.'
                             .format(dt.DateTime.fromHoy(hoy)))

        return self._values[sid][stateid][hoy]

    def getImages(self, hoys, source=None, state=None):
        """Get list of images for an hour in the year."""
        sid = self.sourceId(source)
        # find the state id
        stateid = self.blindStateId(source, state)

        for hoy in hoys:
            if hoy not in self._values[sid][stateid]:
                raise ValueError('Hourly values are not available for {}.'
                                 .format(dt.DateTime.fromHoy(hoy)))

        return tuple(self._values[sid][stateid][hoy] for hoy in hoys)

    def getImageById(self, hoy, sid=None, stateid=None):
        """Get list of images for an hour in the year."""
        if hoy not in self._values[sid][stateid]:
            raise ValueError('Hourly values are not available for {}.'
                             .format(dt.DateTime.fromHoy(hoy)))

        return self._values[sid][stateid][hoy]

    def getImagesById(self, hoys, sid=None, stateid=None):
        """Get list of images for an hour in the year."""
        for hoy in hoys:
            if hoy not in self._values[sid][stateid]:
                raise ValueError('Hourly values are not available for {}.'
                                 .format(dt.DateTime.fromHoy(hoy)))

        return tuple(self._values[sid][stateid][hoy] for hoy in hoys)

    def generateImage(self, hoy, source=None, state=None, mode=0, output=None):
        """Generate the image for an hour of the year for input blindStates."""
        # find the id for source and state
        images = self.getImage(hoy, source, state)
        if mode > 0:
            return images[mode - 1]
        else:
            # generate the image.
            fpt, fpd, fps = images
            if not output:
                output = os.path.join(
                    self.outputFolder,
                    '{}_{:04d}..{}..{}.hdr'.format(mode, int(hoy), source, state)
                )

            ti = PcombImage(inputImageFile=fpt)
            di = PcombImage(inputImageFile=fpd, scalingFactor=-1)
            si = PcombImage(inputImageFile=fps)

            res = Pcomb((ti, di, si), output)
            return res.execute()

    def generateImageById(self, hoy, sid=None, stateid=None, mode=0, output=None):
        """Generate the image for an hour of the year for input blindStates."""
        # find the id for source and state
        images = self.getImageById(hoy, sid, stateid)
        if mode > 0:
            return images[mode - 1]
        else:
            # generate the image.
            fpt, fpd, fps = images
            if not output:
                output = os.path.join(
                    self.outputFolder,
                    '{:04d}..{}..{}.hdr'.format(int(hoy), sid, stateid)
                )

            ti = PcombImage(inputImageFile=fpt)
            di = PcombImage(inputImageFile=fpd, scalingFactor=-1)
            si = PcombImage(inputImageFile=fps)

            res = Pcomb((ti, di, si), output)
            return res.execute()

    def generateImages(self, hoys, source=None, state=None, mode=0, outputs=None):
        """Generate images for several hours of the year for input blindStates."""
        # find the id for source and state
        imageCol = self.getImages(hoys, source, state)
        if not outputs:
            outputs = tuple(
                os.path.join(self.outputFolder,
                             '{}_{:04d}..{}..{}.hdr'.format(mode, int(hoy),
                                                            source, state))
                for hoy in hoys
            )
        if mode > 0:
            return tuple(images[mode - 1] for images in imageCol)
        else:
            results = []
            # generate the image.
            for images, hoy, output in izip(imageCol, hoys, outputs):
                fpt, fpd, fps = images
                ti = PcombImage(inputImageFile=fpt)
                di = PcombImage(inputImageFile=fpd, scalingFactor=-1)
                si = PcombImage(inputImageFile=fps)

                res = Pcomb((ti, di, si), output)
                results.append(res.execute())

            return results

    def generateImagesById(self, hoys, sid=None, stateid=None, mode=0, outputs=None):
        """Generate images for several hours of the year for input blindStates."""
        # find the id for source and state
        imageCol = self.getImagesById(hoys, sid, stateid)
        if not outputs:
            outputs = tuple(
                os.path.join(self.outputFolder,
                             '{}_{:04d}..{}..{}.hdr'.format(mode, int(hoy),
                                                            sid, stateid))
                for hoy in hoys
            )
        if mode > 0:
            return tuple(images[mode - 1] for images in imageCol)
        else:
            results = []
            # generate the image.
            for images, hoy, output in izip(imageCol, hoys, outputs):
                fpt, fpd, fps = images
                ti = PcombImage(inputImageFile=fpt)
                di = PcombImage(inputImageFile=fpd, scalingFactor=-1)
                si = PcombImage(inputImageFile=fps)

                res = Pcomb((ti, di, si), output)
                results.append(res.execute())

            return results

    def generateCombinedImageById(self, hoy, blindsStateIds=None, mode=0, output=None):
        """Get combined value from all sources based on stateId.

        Args:
            hoy: hour of the year.
            blindsStateIds: List of state ids for all the sources for an hour. If you
                want a source to be removed set the state to -1.
            mode: 0 > combined scene, 1 > Default scene, 2 > Direct, 3 > Sun.

        Returns:
            combined image from all sources.
        """
        if not blindsStateIds:
            blindsStateIds = [0] * len(self._sources)

        assert len(self._sources) == len(blindsStateIds), \
            'There should be a state for each source. #sources[{}] != #states[{}]' \
            .format(len(self._sources), len(blindsStateIds))

        imageCol = []
        for sid, stateid in enumerate(blindsStateIds):
            # collect the images for each source
            if stateid == -1:
                pass
            else:
                if hoy not in self._values[sid][stateid]:
                    raise ValueError('Hourly values are not available for {}.'
                                     .format(dt.DateTime.fromHoy(hoy)))
                imageCol.append(self.getImageById(hoy, sid, stateid))

        if not output:
            name = '_'.join('%d_%d' % (sid, stateid)
                            for sid, stateid in enumerate(blindsStateIds))
            output = os.path.join(
                self.outputFolder,
                '{}_{:04d}..{}.hdr'.format(mode, int(hoy), name)
            )

        if mode > 0:
            pcombImages = tuple(PcombImage(inputImageFile=images[mode - 1])
                                for images in imageCol)
        else:
            # the output is going to be the combined of all the sources
            pcombImages = []
            for images in imageCol:
                # generate the image.
                fpt, fpd, fps = images

                ti = PcombImage(inputImageFile=fpt)
                di = PcombImage(inputImageFile=fpd, scalingFactor=-1)
                si = PcombImage(inputImageFile=fps)
                pcombImages.extend((ti, di, si))

        res = Pcomb(pcombImages, output)
        return res.execute()

    def generateCombinedImagesById(self, hoys=None, blindsStateIds=None, mode=0,
                                   outputs=None):
        """Get combined value from all sources based on stateId.

        Args:
            hoys: A collection of hours of the year.
            blindsStateIds: List of state ids for all the sources for input hoys. If you
                want a source to be removed set the state to -1.

        Returns:
            Return a generator for (total, direct) values.
        """
        hoys = hoys or self.hoys
        if not blindsStateIds:
            try:
                hoursCount = len(hoys)
            except TypeError:
                raise TypeError('hoys must be an iterable object: {}'.format(hoys))
            blindsStateIds = [[0] * len(self._sources)] * hoursCount

        assert len(hoys) == len(blindsStateIds), \
            'There should be a list of states for each hour. #states[{}] != #hours[{}]' \
            .format(len(blindsStateIds), len(hoys))

        outputs = outputs or []
        results = []
        for count, hoy in enumerate(hoys):
            imageCol = []
            for sid, stateid in enumerate(blindsStateIds[count]):
                if stateid == -1:
                    continue
                else:
                    if hoy not in self._values[sid][stateid]:
                        raise ValueError('Hourly values are not available for {}.'
                                         .format(dt.DateTime.fromHoy(hoy)))
                    imageCol.append(self.getImageById(hoy, sid, stateid))
            assert imageCol, \
                ValueError('All the state ids cannot be -1.')

            # create outputs
            try:
                output = outputs[count]
            except IndexError:
                name = '_'.join('%d_%d' % (sid, stateid)
                                for sid, stateid in enumerate(blindsStateIds[count]))

                output = os.path.join(
                    self.outputFolder,
                    '{}_{:04d}..{}.hdr'.format(mode, int(hoy), name)
                )

            if mode > 0:
                pcombImages = tuple(PcombImage(inputImageFile=images[mode - 1])
                                    for images in imageCol)
            else:
                # the output is going to be the combined of all the sources
                pcombImages = []
                for images in imageCol:
                    # generate the image.
                    fpt, fpd, fps = images

                    ti = PcombImage(inputImageFile=fpt)
                    di = PcombImage(inputImageFile=fpd, scalingFactor=-1)
                    si = PcombImage(inputImageFile=fps)
                    pcombImages.extend((ti, di, si))

            res = Pcomb(pcombImages, output)
            results.append(res.execute().toRadString())

        return results

    @staticmethod
    def parseBlindStates(blindsStateIds):
        """Parse input blind states.

        The method tries to convert each state to a tuple of a list. Use this method
        to parse the input from plugins.

        Args:
            blindsStateIds: List of state ids for all the sources for an hour. If you
                want a source to be removed set the state to -1. If not provided
                a longest combination of states from sources (window groups) will
                be used. Length of each item in states should be equal to number
                of sources.
        """
        try:
            combs = [list(eval(cc)) for cc in blindsStateIds]
        except Exception as e:
            ValueError('Failed to convert input blind states:\n{}'.format(e))

        return combs

    def ToString(self):
        """Overwrite ToString .NET method."""
        return self.__repr__()

    def __str__(self):
        """String repr."""
        return self.__repr__()

    def __repr__(self):
        """Return analysis points and directions."""
        return 'ImgCol::{}::#{}'.format(self.name, len(self.hoys))
