"""
This file provides an example binding to ESO's RESTful phase 2 programmatic interface.
The data required and returned by many of the API calls is instrument-specific.
In order to fully understand the data and behaviour of the API please consult
the documentation at https://www.eso.org/copdemo/apidoc/
The api URL specified with each API should help to locate the corresponding
API documentation at the above URL.

Unless otherwise mentioned, each API call consistently returns a tuple (data, version):
    * data    - returned data in JSON format
    * version - version of the data, required for future modifications (HTTP ETags are used for this versioning)

___________________________________________________________________________
MIT License
___________________________________________________________________________
Copyright (c) 2021 Thomas Bierwirth, European Southern Observatory

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from __future__ import print_function
import os
import json
import requests
import re

# $Id: p2api.py 267837 2021-10-26 10:13:31Z jpritcha $
P2_API_VERSION = '1.0.5'
__version__=P2_API_VERSION

API_URL = {
    'production'        : 'https://www.eso.org/cop/api/v1',
    'production_lasilla': 'https://www.eso.org/copls/api/v1',
    'demo'              : 'https://www.eso.org/copdemo/api/v1',
}
LOGIN_URL = {
    'production'        : 'https://www.eso.org/cop/api/login',
    'production_lasilla': 'https://www.eso.org/copls/api/login',
    'demo'              : 'https://www.eso.org/copdemo/api/login',
}
P2FC_URL = {
    'production'        : 'https://www.eso.org/p2fc/',
    'production_lasilla': 'https://www.eso.org/p2fc/',
    'demo'              : 'https://www.eso.org/p2fcdemo/',
}

class P2Error(Exception):
    pass

class ApiConnection(object):
# ---------- PUBLIC API ----------
    def __init__(self, *args, **kwargs) :
    #def __init__(self, environment, username, password, debug=False):
        """
        Set environment, log in to the API and obtain access token for further
        calls. Returns authenticated api connection required to invoke other
        API calls.

        Supported environments are
            - 'production'         : for Paranal Observation Preparation
            - 'production_lasilla' : for La Silla Observation Preparation
            - 'demo'               : to experiment with both Paranal and La Silla

        usage:
           ::

              api = p2api.ApiConnection('demo', '52052', 'tutorial')
              api = p2api.ApiConnection('demo', '52052', 'tutorial', True)
              api = p2api.ApiConnection(environment='demo', username='52052', password='tutorial', debug=True)
            or
              api = p2api.ApiConnection(url='https://www.eso.org/copdemo/api/v1', access_token='<access_token>')
              api = p2api.ApiConnection(url='https://www.eso.org/copdemo/api/v1/obsBlocks/{obId}', access_token='<access_token>')
              api = p2api.ApiConnection(url='https://www.eso.org/copdemo/api/v1/containers/{containerId}', access_token='<access_token>')


        """
        if 'environment' in kwargs or len(args) > 0 :
            # Define parameters...
            param_values={}
            required_params=[
                'environment',
                'username',
                'password',
            ]
            optional_params=[
                'debug',
            ]
            optional_param_defaults=[
                False,
            ]

            # Set parameter values from provided arguments...
            for i,k in enumerate(args) :
                param_values[(required_params+optional_params)[i]]=args[i]

            # Check all required parameters have been specified
            required_params_not_specified=[]
            for k in required_params :
                if k not in param_values.keys() :
                    if k in kwargs.keys() :
                        param_values[k]=kwargs[k]
                    else :
                        required_params_not_specified+=['required parameter %s not specified' %(k),]
            if required_params_not_specified != [] :
                raise P2Error(
                    500,
                    'POST',
                    ', '.join(required_params_not_specified)
                    ,
                )
            # Set default values for optional parameters not specified
            for i,k in enumerate(optional_params) :
                if k not in param_values.keys() :
                    param_values[k]=optional_param_defaults[i]
            # Parameters now set...
            self.p2fc_url = P2FC_URL
            self.debug=param_values['debug']
            self.request_count = 0
            if param_values['environment'] not in API_URL.keys() :
                raise P2Error(500, 'POST', param_values['environment'], 'environment not supported')
            self.apiUrl = API_URL[param_values['environment']]
            self.loginUrl = LOGIN_URL[param_values['environment']]
            self.session = self.requests_retry_session()

            r = requests.post(
                self.loginUrl,
                data={
                    'username': param_values['username'],
                    'password': param_values['password'],
                }
            )
            if r.status_code == requests.codes.ok:
                body = r.json()
                self.access_token = body['access_token']
            else:
                raise P2Error(r.status_code, 'POST', self.loginUrl, 'cannot login')

        elif 'url' in kwargs :
            self.debug = kwargs.get('debug') or False
            self.request_count = 0
            url_is_valid=False
            for environment in API_URL.keys() :
                if API_URL[environment] in kwargs['url'] :
                    url_is_valid=True
                    break
            if not url_is_valid :
                raise P2Error(500, 'POST', kwargs['url'], 'Invalid URL')
            self.apiUrl = API_URL[environment]
            self.loginUrl = LOGIN_URL[environment]
            self.access_token = kwargs['access_token']
            self.session = self.requests_retry_session()
        else :
            raise P2Error(500, 'POST', LOGIN_URL[kwargs.get('environment','production')], 'Unknown API init method')

# ---------- RUN-LEVEL APIs ----------
    """
    Still pending implementation:
    New end points for various requests:
        /obsRuns/{runId}/request/instrumentChange
        /obsRuns/{runId}/request/targetChange
        /obsRuns/{runId}/request/waiver
    """
    def getRuns(self):
        """Retrieve observing runs owned by or delegated to logged-in user.

        api: GET /obsRuns

        usage:
           ::

              runs, _ = api.getRuns()
        """
        return self.get('/obsRuns')

    def getRun(self, runId):
        """Get a single observing run.

        api: GET /obsRuns/{runId}

        usage:
           ::

              run, _ = api.getRun(runId)
        """
        return self.get('/obsRuns/%d' % runId)

    def getPhase1Targets(self, runId):
        """Retrieve the list of targets defined in phase 1.

        api: GET /obsRuns/{runId}/phase1/targets

        usage:
           ::

              targets, _ = api.getPhase1Targets(runId)
        """
        return self.get('/obsRuns/%d/phase1/targets' % runId)

    def getBlockedTimes(self, runId):
        """Retrieve a list of blocked times on the telescope in the
        scheduled period of this observing run.

        api: GET /obsRuns/{runId}/phase1/blockedTimes

        usage:
           ::

              targets, _ = api.getBlockedTimes(runId)
        """
        return self.get('/obsRuns/%d/phase1/blockedTimes' % runId)

    def submitRun(self, runId):
        """Submit the observing run to ESO for review.

        api  : POST /obsRuns/{runId}/submit

        usage:
           ::

              api.submitRun(runId)
        """
        return self.post('/obsRuns/%d/submit' % runId)

    def getReadmeSchema(self, runId):
        """Retrieve the schema definition for the ReadMe file of this observing run.

        api: GET /obsRuns/{runId}/readme/schema

        usage:
           ::

              readmeSchema, _ = api.getReadmeSchema(runId)
        """
        return self.get('/obsRuns/%d/readme/schema' % runId)

    def getReadme(self, runId):
        """Retrieve the ReadMe file of this observing run.

        api: GET /obsRuns/{runId}/readme

        usage:
           ::

              readme, readmeVersion = api.getReadme(runId)
        """
        return self.get('/obsRuns/%d/readme' % runId)

    def saveReadme(self, runId, readme, version):
        """
        Update the ReadMe file.

        api: PUT /obsRuns/{runId}/readme.

        usage:
           ::

              readme, readmeVersion = api.saveReadme(runId, readme, version)
        """
        return self.put('/obsRuns/%d/readme' % runId, readme, version)

# ---------- CONTAINER-LEVEL APIs ----------
    def getContainer(self, containerId):
        """Get container information.

        api: GET /containers/{containerId}

        usage:
           ::

              container, containerVersion = api.getContainer(containerId)
        """
        return self.get('/containers/%d' % containerId)

    def saveContainer(self, container, version):
        """Update container information.

        api: PUT /containers/{containerId}

        usage:
           ::

              container, containerVersion = api.getContainer(containerId)
              # modify some container properties ...
              container['userPriority'] = 10
              # save changes
              container, containerVersion = api.saveContainer(container, containerVersion)
        """
        return self.put('/containers/%d' % container['containerId'], container, version)

    def deleteContainer(self, containerId, version):
        """Delete container. The container must be empty.

        api: DELETE /containers/{containerId}

        usage:
           ::

              container, containerVersion = api.getContainer(container)
              api.deleteContainer(container['containerId'], containerVersion)
        """
        return self.delete('/containers/%d' % containerId, etag=version)

    def createItem(self, itemType, containerId, name):
        """Create a new OB, CB, Folder, Group, Concatenation or TimeLink
        at the end of the given container.

        The initial values for the observing constraints of a new OB are those
        specified during phase 1, or the instrument defaults.

        Visitor Mode: Groups, Concatenations and TimeLinks cannot be created.

        Service Mode: Groups, Concatenations and TimeLinks cannot contain other
        containers, only OBs and CBs.

        See also wrappers below to create specific items by name.

        api: POST /containers/{containerId}/items

        usage:
           ::

              ob, obVersion = api.createItem('OB', containerId, 'OliOB')
        """
        return self.post('/containers/%d/items' % containerId, {'itemType': itemType, 'name': name})

    def createOB(self, containerId, name):
        """Create a new Observing Block.

        api: POST /containers/{containerId}/items

        usage:
           ::

              ob, obVersion = api.createOB(containerId, 'OliOB')
        """
        return self.createItem('OB', containerId, name)

    def createCB(self, containerId, name):
        """Create a new Calibration Block.

        api  : POST /containers/{containerId}/items

        usage:
           ::

              cb, cbVersion = api.createCB(containerId, 'OliCB')
        """
        return self.createItem('CB', containerId, name)

    def createFolder(self, containerId, name):
        """Create a new Folder.

        api: POST /containers/{containerId}/items

        usage:
           ::

              fld, fldVersion = api.createFolder(containerId, 'OliFolder')
        """
        return self.createItem('Folder', containerId, name)

    def createGroup(self, containerId, name):
        """Create a new Group.

        api: POST /containers/{containerId}/items

        usage:
           ::

              grp, grpVersion = api.createGroup(containerId, 'OliGroup')
        """
        return self.createItem('Group', containerId, name)

    def createConcatenation(self, containerId, name):
        """Create a new Concatenation.

        api: POST /containers/{containerId}/items

        usage:
           ::

              con, conVersion = api.createConcatenation(containerId, 'OliConcatenation')
        """
        return self.createItem('Concatenation', containerId, name)

    def createTimeLink(self, containerId, name):
        """Create a new TimeLink

        api: POST /containers/{containerId}/items

        usage:
           ::

              tl, tlVersion = api.createTimeLink(containerId, 'OliTimeLink')
        """
        return self.createItem('TimeLink', containerId, name)

    def getItems(self, containerId):
        """ Get ordered list of OBs and containers inside a container.

        api: GET /containers/{containerId}/items

        usage:
           ::

              items, itemsVersion = api.getItems(containerId)
        """
        return self.get('/containers/%d/items' % containerId)

    def reorderItems(self, containerId, items, version):
        """Change order of OBs and containers inside a container.

        api: PUT /containers/{containerId}/items

        usage:
           ::

              items, itemsVersion = api.getItems(containerId)
              # modify items order ...
              # save changes
              items, itemsVersion = api.reorderItems(containerId, items, itemsVersion)
        """
        return self.put('/containers/%d/items' % containerId, items, version)

    def moveFolder(self, folderId, containerId):
        """Move existing folder into destination container.

        api: POST /containers/{containerId}/items/append

        usage:
           ::

              api.moveFolder(folderId, containerId)
        """
        return self.post('/containers/%d/items/append' % containerId,
                         {'itemType': 'Folder', 'containerId': folderId})

    def moveGroup(self, groupId, containerId):
        """Move existing group into destination container.

        api: POST /containers/{containerId}/items/append

        usage:
           ::

              api.moveGroup(groupId, containerId)
        """
        return self.post('/containers/%d/items/append' % containerId,
                         {'itemType': 'Group', 'containerId': groupId})

    def moveConcatenation(self, concatenationId, containerId):
        """Move existing concatenation into destination container.

        api: POST /containers/{containerId}/items/append

        usage:
           ::

              api.moveConcatenation(concatenationId, containerId)
        """
        return self.post('/containers/%d/items/append' % containerId,
                         {'itemType': 'Concatenation', 'containerId': concatenationId})

    def moveTimeLink(self, timeLinkId, containerId):
        """Move existing timelink into destination container.

        api: POST /containers/{containerId}/items/append

        usage:
           ::

              api.moveTimeLink(folderId, containerId)
        """
        return self.post('/containers/%d/items/append' % containerId,
                         {'itemType': 'TimeLink', 'containerId': timeLinkId})

    def moveOB(self, obId, containerId):
        """Move existing OB into destination container.

        api: POST /containers/{containerId}/items/append

        usage:
           ::

              api.moveOB(obId, containerId)
        """
        return self.post('/containers/%d/items/append' % containerId,
                         {'itemType': 'OB', 'obId': obId})

    def moveCB(self, obId, containerId):
        """Move existing CB into destination container.

        api: POST /containers/{containerId}/items/append

        usage:
           ::

              api.moveCB(obId, containerId)
        """
        return self.post('/containers/%d/items/append' % containerId,
                         {'itemType': 'CB', 'obId': obId})

    def getOBSummary(self, containerId):
        """Get more detailed summary of all OBs in a container

        api: GET /containers/{containerId}/items/summary

        usage:
           ::

              api.getOBSummary(containerId)
        """
        return self.get('/containers/%d/items/summary' % containerId)

    def verifyContainer(self, containerId, submit):
        """Verify a Group, Concatenation or TimeLink.

        If submit is false, a Group, Concatenation, or TimeLink can be verified
        in any container status. If submit is true, the container must have
        container status "-" or "P".

        OBs inside the container must be verified first, i.e. they have a status
        of "D" or later.

        The instrument-specific verification scripts for a container are executed.
        If submit is true and verification is successful, the container status
        is changed to "D".

        A change of the container status will invalidate the ETag of the container.

        api: POST /containers/{containerId}/verify

        usage:
           ::

              response, _ = api.verifyContainer(containerId, True)
              if response['observable']:
                 print('Your container is observable!')
              else:
                 print('Your container is >>not observable<<. See messages below.')
                 print(' ')
                 print(' '.join(response['messages']))
        """
        return self.post('/containers/%d/verify' % containerId, {'submit': submit})

    def reviseContainer(self, containerId):
        """Open Group/Concatenation/TimeLink for further changes.

        Change the container status back to "P".
        This is the counterpart to verification with submission.

        api: POST /containers/{containerId}/revise

        usage:
           ::

              api.reviseContainer(containerId)
        """
        return self.post('/containers/%d/revise' % containerId)

    def exportContainer(self, containerId, filename):
        """Export this container into a ZIP file.

        api: GET /containers/{containerId}/export

        usage:
           ::

              api.exportContainer(containerId, 'myContainer.zip')
        """
        self.downloadBinaryFile('/containers/%d/export' % containerId, filename)

# ---------- OB-LEVEL APIs ----------
    def getOB(self, obId):
        """Get existing OB or CB.

        api: GET /obsBlocks/{obId}

        usage:
           ::

              ob, obVersion = api.getOB(obId)
        """
        return self.get('/obsBlocks/%d' % obId)

    def saveOB(self, ob, version):
        """Update existing OB or CB.

        The format of an OB is instrument-specific and differs for OBs and CBs.
        The instrument defines the applicable observingConstraints.
        A CB does not have a target. The properties itemType, obId, obStatus,
        ipVersion, exposureTime and executionTime cannot be changed.
        The OB must have the latest ipVersion. Refer to the API spec
        for further updating constraints.

        api: PUT /obsBlocks/{obId}

        usage:
           ::

              ob, obVersion = api.getOB(obId)
              # modify some OB properties ...
              ob['userPriority'] = 42
              ob['target']['name']         = 'M 32 -- Interacting Galaxies'
              ob['target']['ra']           = '00:42:41.825'
              ob['target']['dec']          = '-60:51:54.610'
              ob['constraints']['name']    = 'My hardest constraints ever'
              ob['constraints']['airmass'] = 1.3
              # save changes
              ob, obVersion = api.saveOB(ob, obVersion)
        """
        return self.put('/obsBlocks/%d' % ob['obId'], ob, version)

    def deleteOB(self, obId, version):
        """Delete existing OB or CB.

        Visitor Mode: The OB must have never been executed.

        Service Mode: The OB must have status (-), (P) or (D) and must have never been executed.

        api: DELETE /obsBlocks/{obId}

        usage:
           ::

              ob, obVersion = api.getOB(obId)
              api.deleteOB(ob, obVersion)
        """
        return self.delete('/obsBlocks/%d' % obId, etag=version)

    def verifyOB(self, obId, submit):
        """Verify OB and submit it for observation.

        If submit is false, an OB can be verified in any status. If submit is
        true, a loose service mode OB must be in status "P" or "-" and a visitor
        mode OB must be in a status other than "S", "A", "X", or "+".

        api: POST /obsBlocks/{obId}/verify

        usage:
           ::

              response, _ = api.verifyOB(obId, True)
              if response['observable']:
                 print('Your OB' , obId, ob['name'], 'is observable!')
              else:
                 print('OB', obId, 'is >>not observable<<. See messages below.')
                 print(' ')
                 print(' '.join(response['messages']))
        """
        return self.post('/obsBlocks/%d/verify' % obId, {'submit': submit})

    def reviseOB(self, obId):
        """Back to the drawing board.

        Change the OB status back to "P", i.e. mark it as not observable.
        This is the counterpart to verification with submission.

        A visitor mode OB can be in any status. The status is changed to "P".
        The OB will be removed from any visitor execution sequences because
        it is no longer in an observable status; this changes the ETag of
        the affected visitor execution sequences.

        A service mode OB can only be revised in status "D". The status is
        changed to "P". If the OB is a member of a Group, Concatenation or
        TimeLink with container status other than "-" or "P", the container
        status will be changed to "P".

        This call invalidates the ETag of the OB, and possibly of the parent
        container, if the container status was changed.

        api: POST /obsBlocks/{obId}/revise

        usage:
           ::

              pi.reviseOB(obId)
        """
        return self.post('/obsBlocks/%d/revise' % obId)

    def duplicateOB(self, obId, containerId=0):
        """Duplicate OB.

        Create a new OB or CB identical to this one in the same or a different
        container. The new OB is appended at the end of the container. The
        destination may be in a different observing run of the same instrument.

        api: POST /obsBlocks/{obId}/duplicate

        usage:
           ::

              duplicatedOB, duplicatedOBVersion = api.duplicateOB(obId)
              duplicatedOB, duplicatedOBVersion = api.duplicateOB(obId, containerId)
        """
        data = {}
        if containerId > 0:
            data = {'containerId': containerId}
        return self.post('/obsBlocks/%d/duplicate' % obId, data)

    def migrateOB(self, obId, dryRun):
        """Migrate OB to latest instrument package.

        api: POST /obsBlocks/{obId}/migrate

        usage:
           ::

              result, _ = api.migrateOB(obId, false)
              result, _ = api.migrateOB(obId, true)
        """
        return self.post('/obsBlocks/%d/migrate' % obId, {'dryRun': dryRun})

    def executionTime(self, Id, itemType=None):
        """Compute the execution time for the OB, or all OBs in or below a container.

        api: POST /obsBlocks/{Id}/executionTime

        usage:
           ::

              obInfo = api.executionTime(Id)
              containersInfo = api.executionTime(Id)
              containersInfo = api.executionTime(Id, itemType='Folder')
              containersInfo = api.executionTime(Id, itemType='Group')

        If Id is a an obId, a obInfo dictionary will be returned.
        If Id is a containerId (Folder, Group, Concatenation, TimeLink) a list
        of obInfo and/or containerInfo dictionaries will be returned. A containerInfo
        dictionary provides info about the container, and the OBs contained in that
        container. Folders do not generate containerInfo dictionaries.
        """
        if itemType in [None, 'OB'] :
            try :
                return self.post('/obsBlocks/%d/executionTime' % Id)[0]
            except :
                # We assume it failed because Id is not an OB,
                # thus it must be a container, so we work through the container
                pass
        obsInfo=[]
        c,_ = self.getContainer(Id)
        if c['itemType'] in ['Group','Concatenation','TimeLink',] :
            c['exposureTime']=0
            c['executionTime']=0
            c['obs']=self.post('/containers/%d/items/executionTimes' % Id)[0]
            for ob in c['obs'] :
                c['exposureTime']+=ob['exposureTime']
                c['executionTime']+=ob['executionTime']
            obsInfo+=[c,]
        else:
            # Id must be a folder...
            items, _ = self.getItems(Id)
            for item in items :
                obsInfo+=[self.executionTime(item.get('obId',item.get('containerId')), itemType=item['itemType'])]
        return obsInfo

    def exportOB(self, obId, filename):
        """Export this OB into a ZIP file.

        api: GET /obsBlocks/{obId}/export

        usage:
           ::

              api.exportOB(obId, 'myOB.zip')
        """
        self.downloadBinaryFile('/obsBlocks/%d/export' % obId, filename)

    def getOBExecutions(self, obId, night):
        """Get executions during a given night.

        api: GET /obsBlocks/{obId}/executions

        usage:
           ::

              obExecutions, _ = getOBExecutions(obId, '2018-01-01')
        """
        return self.get('/obsBlocks/%d/executions?night=%s' % (obId, night))

    def getNightExecutions(self, instrument, night ):
        """Get executions during a given night for a specific instrument

        api: GET /executions/{instrument}

        usage:
           ::

              executions, _ = api.getNightExecutions(instrument, night)
              executions, _ = api.getNightExecutions(instrument, '2016-01-19')
        """
        return self.get('/executions/%s?night=%s' %(instrument,night))

    def getOBCompletelyFilledIn(self, obId):
        """Check that the OB's templates are completely filled in.

        Performs a quick check that there are neither missing templates
        nor missing parameters on this OB.

        This is not a full validation.

        api: GET /obsBlocks/{obId}/templates/completelyFilledIn

        usage:
           ::

              response, _ = api.getOBCompletelyFilledIn(obId)
              print('OB complete:', response['complete'])
        """
        return self.get('/obsBlocks/%d/templates/completelyFilledIn' % obId)

    def getAbsoluteTimeConstraints(self, obId):
        """Get list of absolute time constraints.

        The list is sorted in ascending order by from.
        Date and time are in ISO-8601 format for the UTC timezone.
        A CB does not have absolute time constraints and returns an empty list.

        api: GET /obsBlocks/{obId}/timeConstraints/absolute

        usage:
           ::

              absTCs, atcVersion = api.getAbsoluteTimeConstraints(obId)
        """
        return self.get('/obsBlocks/%d/timeConstraints/absolute' % obId)

    def saveAbsoluteTimeConstraints(self, obId, timeConstraints, version):
        """Set list of absolute time constraints.

        Date and time are in ISO-8601 format and must use UTC timezone.
        Time intervals must not overlap and from must be earlier than to.

        api: PUT /obsBlocks/{obId}/timeConstraints/absolute

        usage:
           ::

              absTCs, atcVersion = api.getAbsoluteTimeConstraints(obId)
              api.saveAbsoluteTimeConstraints(obId,[
                {
                    'from': '2017-09-01T00:00',
                    'to': '2017-09-30T23:59'
                },
                {
                    'from': '2017-11-01T00:00',
                    'to': '2017-11-30T23:59'
                }
              ], atcVersion)
        """
        return self.put('/obsBlocks/%d/timeConstraints/absolute' % obId, timeConstraints, version)

    def getSiderealTimeConstraints(self, obId):
        """Get list of sidereal time constraints.

        The list is sorted in ascending order by from.
        A CB does not have sidereal time constraints and returns an empty list.

        api: GET /obsBlocks/{obId}/timeConstraints/sidereal

        usage:
           ::

              sidTCs, stcVersion = api.getSiderealTimeConstraints(obId)
        """
        return self.get('/obsBlocks/%d/timeConstraints/sidereal' % obId)

    def saveSiderealTimeConstraints(self, obId, timeConstraints, version):
        """Set list of sidereal time constraints.

        Time intervals must not overlap. A time interval ending at the starting time
        of another is considered an overlap; avoid this by combining the intervals
        into a single one.

        There can be a single time interval ending at 24:00; it will not overlap
        a time interval starting at 0:00. An interval ending at 24:00 and one
        starting at 00:00 will be combined into a single interval.

        24:00 cannot be used as starting time, and 00:00 cannot be used
        as ending time.

        api: PUT /obsBlocks/{obId}/timeConstraints/sidereal

        usage:
           ::

              sidTCs, stcVersion = api.getSiderealTimeConstraints(obId)
              api.saveSiderealTimeConstraints(obId,[
                {
                    'from': '00:00',
                    'to': '01:00'
                },
                {
                    'from': '03:00',
                    'to': '05:00'
                }
              ], stcVersion)
        """
        return self.put('/obsBlocks/%d/timeConstraints/sidereal' % obId, timeConstraints, version)

    def createTemplate(self, obId, name):
        """Attach a new template.

        An OB can have only one acquisition template. Attempting to add a
        second one will result in an error.

        The OB must have the latest ipVersion.

        Visitor Mode: The OB can be changed in any status.

        Service Mode: The OB must have status (-) or (P).

        api: POST /obsBlocks/{obId}/templates

        usage:
           ::

              tpl, tplVersion = api.createTemplate(obId, 'UVES_blue_acq_slit')
        """
        return self.post('/obsBlocks/%d/templates' % obId, {'templateName': name})

    def getTemplates(self, obId):
        """Get all attached templates.

        api: GET /obsBlocks/{obId}/templates

        usage:
           ::

              templates, templatesVersion = api.getTemplates(obId)
              for t in templates:
                 print ('template found:', t['templateName'])
        """
        return self.get('/obsBlocks/%d/templates' % obId)

    def reorderTemplates(self, obId, templates, version):
        """Change order of attached templates.

        The list must contain the same items as in the previous GET request.
        Only the order can be changed. Templates must be explicitly added
        with a POST request or deleted with a DELETE request. If there is
        an acquisition template, it must be the first in the list.

        The OB must have the latest ipVersion.

        Visitor Mode: The OB can be changed in any status.

        Service Mode: The OB must have status (-) or (P).

        api: PUT /obsBlocks/{obId}/templates

        usage:
           ::

              tpls, tplsVersion = api.getTemplates(obId)
              # change order of tpls ...
              tpls, tplsVersion = api.reorderTemplates(obId, tpls, tplsVersion)
        """
        return self.put('/obsBlocks/%d/templates' % obId, templates, version)

    def getTemplate(self, obId, templateId):
        """Get existing template.

        A parameter value may be null if there is no default value and a
        value was never set.

        For parameters of type 'paramfile' or 'file' a string is returned.
        For a 'paramfile' this is the value of PAF.NAME in the PAF header;
        for a 'file' the first few characters are returned.
        File parameters are set with a separate call.

        api: GET /obsBlocks/{obId}/templates/{templateId}

        usage:
           ::

              tpl, tplVersion = api.getTemplate(obId, templateId)
        """
        return self.get('/obsBlocks/%d/templates/%d' % (obId, templateId))

    def setTemplateParams(self, obId, template, params, version):
        """Helper API to make it easier to update template parameters.
           Uses saveTemplate() under the hood.


        usage:
           ::

              tpl, tplVersion = api.createTemplate(obId, 'UVES_blue_acq_slit')
              tpl, tplVersion  = api.setTemplateParams(obId, tpl, {
                'TEL.GS1.ALPHA': '11:22:33.000',
                'INS.COLL.NAID': 'COLL_SR+7',
                'INS.DPOL.MODE': 'ON'
              }, tplVersion)
        """
        for p in template['parameters']:
            p['value'] = params.get(p['name'], p['value'])
        return self.saveTemplate(obId, template, version)

    def saveTemplate(self, obId, template, version):
        """Update existing template.

        The templateId, templateName and type cannot be changed.

        When GET returns a value of null, it can be changed to a proper value
        (or left at null). But a proper value cannot be unset to null.

        File parameters must be set with a separate call; the string value
        returned from GET cannot be changed.

        The OB must have the latest ipVersion.

        Visitor Mode: The OB can be changed in any status.

        Service Mode: The OB must have status (-) or (P).

        api: PUT /obsBlocks/{obId}/templates/{templateId}

        usage:
           ::

              It is recommended to use setTemplateParams() instead
        """
        return self.put('/obsBlocks/%d/templates/%d' % (obId, template['templateId']), template, etag=version)

    def getFileParam(self, obId, templateId, param, filename):
        """Get value of a template parameter of type "file" or "paramfile".

        api: GET /obsBlocks/{obId}/templates/{templateId}/{fileParameter}

        usage:
           ::

              _, version = api.getFileParam(obId, templateId, 'SEQ.REF.FILE1', myFile.paf')
        """
        return self.downloadTextFile('/obsBlocks/%d/templates/%d/%s' % (obId, templateId, param), filename)

    def saveFileParam(self, obId, templateId, param, filename, version):
        """Set value of a parameter of type "file" or "paramfile".

        api: PUT /obsBlocks/{obId}/templates/{templateId}/{fileParameter}

        usage:
           ::

              _, version = api.getFileParam(obId, templateId, 'SEQ.REF.FILE1', myFile.paf')
              api.saveFileParam(obId, templateId, 'SEQ.REF.FILE1', newFile.paf', version)
        """
        return self.uploadFile('PUT', '/obsBlocks/%d/templates/%d/%s' % (obId, templateId, param), filename,
                               'text/plain', version)

    def deleteTemplate(self, obId, templateId, version):
        """Delete existing template.

        The OB must have the latest ipVersion.

        Visitor Mode: The OB can be changed in any status.

        Service Mode: The OB must have status (-) or (P).

        api: DELETE /obsBlocks/{obId}/templates/{templateId}

        usage:
           ::

              _, tplVersion = api.getTemplate(obId, templateId)
              api.deleteTemplate(obId, templateId, tplVersion)
        """
        return self.delete('/obsBlocks/%d/templates/%d' % (obId, templateId), etag=version)

    def duplicateTemplate(self, obId, templateId, destinationObId=0):
        """Duplicate this template.

        Create a new template identical to this one in this or a different OB.
        The new template is appended at the end of the target OB's template list.

        The new template will have a new templateId. All other fields, including
        any file and paramfile parameters, will be the same as in the original template.

        An OB can have only one acquisition template. Attempting to add a second
        one will result in an error.

        api: POST /obsBlocks/{obId}/templates/{templateId}/duplicate

        usage:
           ::

              duplicatedTemplate, duplicatedTemplateVersion = api.duplicateTemplate(obId, templateId)
              duplicatedTemplate, duplicatedTemplateVersion = api.duplicateTemplate(obId, templateId, destinationObId)
        """
        data = {}
        if destinationObId > 0:
            data = {'obId': destinationObId}
        return self.post('/obsBlocks/%d/templates/%d/duplicate' % (obId, templateId), data)

    def getEphemerisFile(self, obId, filename):
        """Get the ephemeris file of this OB and save it into the given filename.

        If the ephemeris file was never saved, or was deleted, an empty file
        is returned.

        api: GET /obsBlocks/{obId}/ephemeris

        usage:
           ::

              _, ephVersion = api.getEphemerisFile(obId, 'ephem.txt')
        """
        url = '/obsBlocks/%d/ephemeris' % obId
        return self.downloadTextFile(url, filename)

    def saveEphemerisFile(self, obId, filename, version):
        """Save the ephemeris file of this OB.

        A CB cannot have an ephemeris file.

        Service Mode: The OB must have status (-) or (P).

        api: PUT /obsBlocks/{obId}/ephemeris

        usage:
           ::

              _, ephVersion = api.getEphemerisFile(obId, 'delete_me.txt')
              _, ephVersion = api.saveEphemerisFile(obId, 'ephem.txt', ephVersion)
        """
        return self.uploadFile('PUT', '/obsBlocks/%d/ephemeris' % obId, filename,
                               'text/plain', version)

    def deleteEphemerisFile(self, obId, version):
        """Delete the ephemeris file of this OB.

        Service Mode: The OB must have status (-) or (P).

        api: DELETE /obsBlocks/{obId}/ephemeris

        usage:
           ::

              _, ephVersion = api.getEphemerisFile(obId, 'delete_me.txt')
              api.deleteEphemerisFile(obId, ephVersion)
        """
        return self.request('DELETE', '/obsBlocks/%d/ephemeris' % obId, etag=version)

    def getFindingChartNames(self, obId):
        """List attached finding charts.

        Returns the list of names of the attached finding charts in the order
        of their index. If no finding charts are attached, an empty list will
        be returned.

        api: GET /obsBlocks/{obId}/findingCharts

        usage:
           ::

              fcNames, _ = api.getFindingChartNames(obId)
        """
        return self.get('/obsBlocks/%d/findingCharts' % obId)

    def addFindingChart(self, obId, filename):
        """Attach a new finding chart in format image/jpeg.

        Up to 5 finding charts can be attached to a single OB.
        The maximum file size is 1MB (2^20 bytes).

        The OB must have the latest ipVersion.

        Service Mode: The OB must have status (-) or (P).

        api: POST /obsBlocks/{obId}/findingCharts

        usage:
           ::

              api.addFindingChart(obId, filename)
        """
        return self.uploadFile('POST', '/obsBlocks/%d/findingCharts' % obId, filename,
                               'image/jpeg')

    def generateFindingChart(
            self,
            obId,
            obs_date=None,
            stretch=None,
            exponent=None,
            pmin=None,
            pmax=None,
            GAIA_im_IQ=None,
            GAIA_im_noise=None,
            survey=None,
            bkg_image=None,
            bkg_lam=None,
            c_stretch=None,
            c_exponent=None,
            c_pmin=None,
            c_pmax=None,
            c_GAIA_im_IQ=None,
            c_GAIA_im_noise=None,
        ):
        """
        Generate new finding chart(s) in format image/jpeg using ESO's p2fc service.

        If the JPG creation is successful, then, and only then will ANY and ALL
        existing p2fc generated FCs will be removed, the new set of 2 (or 3 if a
        non-default survey or bkg_image is provided) will then be attached. If
        for whatever reason the FC JPG creation process fails, any FC JPGs
        already attached to the OB are left untouched.

        The OB must have the latest ipVersion.

        Service Mode: The OB must have status (-) or (P).

        obs_date: must be interpretable by: , e.g. '2019-10-01 02:03:04 UTC'

        bkg_image: should be a local FITS file

        bkg_lam: discription of the bandpass of the image, only needed if file
        Primary header does not include a keyword BANDPASS or FILTER or is not
        a 'standard' ESO or GEMINI image.

        survey: a SkyView supported image survey providing FITS

        pmin, pmax, stretch & exponent and c_pmin, c_pmax, c_stretch &
        c_exponent are passed directly to the APLPY FITSFigure.show_grayscale
        method,see
          https://aplpy.readthedocs.io/en/stable/api/aplpy.FITSFigure.html#aplpy.FITSFigure.show_grayscale
        for details.

        pmin, pmax, stretch & exponent are applied to BOTH default FCs.

        c_pmin, c_pmax, c_stretch & c_exponent are applied to and and all
        custom FCs.

        GAIA_im_IQ [arcsec] & GAIA_im_noise affect the GAIA pseudo images used
        for insets and if survey='Gaia' is used.

        GAIA_im_noise is a dimensionless factor, with the noise computed via the
        numpy method random.normal(loc,scale) with loc=0.0 and:
          scale=GAIA_im_noise*<brightest_flux_value_in_pseudo_image> The default
        value is (as at 2020-01): 1e-6
        Together with pmin and pmax this parameter gives (some) control over the
        relative appearance of stars of different brightness, and can thus be helpful
        to (for example) highlight faint, but not insignificant, field star(s).

        GAIA_im_IQ & GAIA_im_noise are used for any and all Gaia pseudo images
        associated with the default FCs.

        c_GAIA_im_IQ & c_GAIA_im_noise are the equivalents for any and all Gaia
        pseudo images associated with the custom FCs.

        returns: data
            data : None or json structure, possibly with warning messages.

        usage:
           ::
              data = api.generateFindingChart(obId)
              data = api.generateFindingChart(obId, obs_date='2020-01-01 05:30:00 UTC')
              data = api.generateFindingChart(obId, obs_date='2020-01-01 05:30:00 UTC', pmin=2.5, pmax=99., stretch='arcsinh')
              data = api.generateFindingChart(obId, bkg_image='myobject.fits')
              data = api.generateFindingChart(obId, obs_date='2020-01-01 05:30:00 UTC', bkg_image='myobject.fits')
              data = api.generateFindingChart(obId, survey='2MASS-K')
              data = api.generateFindingChart(obId, obs_date='2020-01-01 05:30:00 UTC', survey='2MASS-K')
              data = api.generateFindingChart(obId, obs_date='2020-01-01 05:30:00 UTC', survey='2MASS-K', c_stretch='sqrt', c_pmin=10., c_pmax=90. )
        """

        data = {
            'url': self.apiUrl + '/obsBlocks/%d' % obId,
            'access_token': self.access_token,
            'obsdate': obs_date,
            'exponent': exponent,
            'pmin': pmin,
            'pmax': pmax,
            'GAIA_im_IQ': GAIA_im_IQ,
            'GAIA_im_noise': GAIA_im_noise,
            'bkg_lam': bkg_lam,
            'survey': survey,
            'c_stretch': c_stretch,
            'c_exponent': c_exponent,
            'c_pmin': c_pmin,
            'c_pmax': c_pmax,
            'c_GAIA_im_IQ': c_GAIA_im_IQ,
            'c_GAIA_im_noise': c_GAIA_im_noise,
        }
        files=None
        if bkg_image is not None :
            if os.path.exists(bkg_image) :
                files={
                    'bkg_image_fits_file': (
                        os.path.basename(bkg_image),
                        open(bkg_image, 'rb'),
                        'image/fits',
                        data,
                    )
                }
                data=None
            else :
                raise P2Error(404, 'POST', self.p2fc_url, "Could not find bkg_image %s" %(bkg_image))
        return self.p2fc_request('POST', data=data, files=files)


    def bkg_image_get_ob_info(
            self,
            obId,
        ):
        """
        Get the current background image settings for the specified OB

        returns: data
            data : None or an <ob_info> json structure, possibly with warning messages.

        usage:
           ::
              bkg_image_info = api.bkg_image_get_ob_info(obId)
        """
        ob_url=self.apiUrl + '/obsBlocks/%d' % obId
        return self.p2fc_request('GET', 'bkg_image?url=%s&access_token=%s&mode=%s' %(ob_url, self.access_token, 'get_ob'))


    def bkg_image_get_ob_image_list(
            self,
            obId,
        ):
        """
        Get the list of currently available background images compatible with the specified OB

        returns: data
            data : None or an <ob_image_list> json structure, possibly with warning messages.

        usage:
           ::
              bkg_image_list = api.bkg_image_get_ob_image_list(obId)
        """
        ob_url=self.apiUrl + '/obsBlocks/%d' % obId
        return self.p2fc_request('GET','bkg_image?url=%s&access_token=%s&mode=%s' %(ob_url, self.access_token, 'get_ob_image_list'))


    def bkg_image_set_ob_info(
            self,
            obId,
            info,
        ):
        """
        Set the current background image settings for the specified OB

        The specified info should be one of:
            - default
            - gaia
            - survey|<survey_name>, e.g. 'survey|2MASS-K'
            - eso_im|<DPid>, e.g. 'eso_im|ADP.2015-05-11T10:19:53.607
            - user_bkg_image|<fits_hash>, e.g. 'user_bkg_image|00c98a6dde73f309f058378399cad019f8405603c63d74b5f2ba342a8ae0a8f1'

        returns: data
            data : None or an <ob_info> json structure, possibly with warning messages.

        usage:
           ::
              bkg_image_info = api.bkg_image_set_ob_info(obId, 'default')
              bkg_image_info = api.bkg_image_set_ob_info(obId, 'gaia')
              bkg_image_info = api.bkg_image_set_ob_info(obId, 'survey|2MASS-K')
              bkg_image_info = api.bkg_image_set_ob_info(obId, 'eso_im|ADP.2015-05-11T10:19:53.607')
              bkg_image_info = api.bkg_image_set_ob_info(obId, 'user_bkg_image|00c98a6dde73f309f058378399cad019f8405603c63d74b5f2ba342a8ae0a8f1')

              bkg_image_list = api.bkg_image_get_ob_image_list(obId)
              first_image=list(bkg_image_list.keys())[0]
              fits_hash=bkg_image_list[first_image]['fits_hash']
              bkg_image_info = api.bkg_image_set_ob_info(obId, 'user_bkg_image|%s' %(fits_hash))
        """
        data = {
            'url': self.apiUrl + '/obsBlocks/%d' % obId,
            'access_token': self.access_token,
            'mode': "set_ob_info",
            'value': info,
        }
        return self.p2fc_request('POST', data=data)


    def bkg_image_upload(
            self,
            obId,
            bkg_image,
            bkg_lam=None,
        ):
        """
        Upload a background image for future use with the specified OB

        bkg_image: a local FITS file

        bkg_lam: discription of the bandpass of the image, only needed if file
        Primary header does not include a keyword BANDPASS or FILTER or is not
        a 'standard' ESO or GEMINI image.

        returns: data
            data : None or an <ob_info> json structure, possibly with warning messages.

        usage:
           ::
              bkg_image_info = api.bkg_image_upload(obId 'ADP.2015-05-11T10:19:53.607.fits')
              bkg_image_info = api.bkg_image_upload(obId 'my_image.fits', bkg_lam='my_special_filter:')
        """
        if os.path.exists(bkg_image) :
            files={
                'bkg_image_fits_file': (
                    os.path.basename(bkg_image),
                    open(bkg_image, 'rb'),
                    'image/fits',
                    {
                        'url': self.apiUrl + '/obsBlocks/%d' % obId,
                        'access_token': self.access_token,
                        'mode': "upload_bkg_image",
                        'bkg_lam': bkg_lam,
                    },
                )
            }
        else :
            raise P2Error(404, 'POST', self.p2fc_url, "Could not find bkg_image %s" %(bkg_image))

        return self.p2fc_request('POST', files=files)

    def bkg_image_delete(
            self,
            obId,
            fits_hash,
        ):
        """
        Delete the specified image for the specified OB

        fits_hash: as provided by e.g. bkg_image_get_info(obId)

        returns: data
            data : None or an <ob_image_list> json structure, possibly with warning messages.

        usage:
           ::
              bkg_image_info = api.bkg_image_delete(obId, 'user_bkg_image|00c98a6dde73f309f058378399cad019f8405603c63d74b5f2ba342a8ae0a8f1')

              bkg_image_list = api.bkg_image_get_ob_image_list(obId)
              first_image=list(bkg_image_list.keys())[0]
              fits_hash=bkg_image_list[first_image]['fits_hash']
              bkg_image_list = api.bkg_image_delete(obId, 'user_bkg_image|%s' %(fits_hash))
        """
        ob_url=self.apiUrl + '/obsBlocks/%d' % obId
        return self.p2fc_request('DELETE', 'bkg_image_delete?url=%s&access_token=%s&fits_hash=%s' %(ob_url, self.access_token, fits_hash))


    def p2fc_request(self, method, url='', data=None, files=None) :
        r = self.session.request(method, "%s/%s" %(self.p2fc_url, url), data=data, files=files)

        content_type = r.headers['Content-Type'].split(';')[0]
        # handle response
        if 200 <= r.status_code < 300:
            if content_type == 'application/json':
                data = r.json()
                return data
            return None
        elif content_type == 'application/json' and 'error' in r.json():
            raise P2Error(r.status_code, 'POST', self.p2fc_url, r.json()['error'])
        else:
            raise P2Error(r.status_code, 'POST', self.p2fc_url, r.text)


    def getFindingChart(self, obId, index, filename):
        """Download finding chart save it into the given filename.

        api: GET /obsBlocks/{obId}/findingCharts/{index}

        usage:
           ::

              api.getFindingChart(obId, 1, 'fc1.jpg')
        """
        url = '/obsBlocks/%d/findingCharts/%d' % (obId, index)
        return self.downloadBinaryFile(url, filename)

    def deleteFindingChart(self, obId, index):
        """Delete finding chart.

        The finding chart at the given index is deleted.
        Finding charts with a higher index 'slide down',
        i.e. finding charts are always numbered consecutively
        starting with 1.

        The OB must have the latest ipVersion.

        Service Mode: The OB must have status (-) or (P).

        api: DELETE /obsBlocks/{obId}/findingCharts/{index}

        usage:
           ::

              api.deleteFindingChart(obId, 1)
        """
        return self.delete('/obsBlocks/%d/findingCharts/%d' % (obId, index))

    def duplicateFindingChart(self, obId, index, destinationObId):
        """Duplicate this finding chart to another OB.

       Attach this finding chart to a different OB.
       The finding chart is appended at the end of the target OB's
       finding chart list.

        The target OB must have the latest ipVersion.

        Visitor Mode: The target OB can have any status.

        Service Mode: The target OB must have status (-) or (P).

        api: POST /obsBlocks/{obId}/findingCharts/{index}/duplicate

        usage:
           ::

              api.duplicateFindingChart(obId, 1, destinationObId)
        """
        return self.post('/obsBlocks/%d/findingCharts/%d/duplicate' % (obId, index), {'obId': destinationObId})

    def getOBSchedulingInfo(self, obId):
        """Get OB scheduling information.

        api: GET /obsBlocks/{obId}/schedule

        usage:
           ::

               obInfo, obInfoVersion = api.getOBSchedulingInfo(obId)
        """
        return self.get('/obsBlocks/%d/schedule' % obId)

    def saveOBSchedulingInfo(self, obId, obInfo, version):
        """Update OB scheduling information.

        api: PUT /obsBlocks/{obId}/schedule

        usage:
           ::

               obInfo, obInfoVersion = api.getOBSchedulingInfo(obId)
               # change something
               obInfo['targetName'] = 'My Best Target'
               api.saveOBSchedulingInfo(obId, obInfo, obInfoVersion)
        """
        return self.put('/obsBlocks/%d/schedule' % obId, obInfo, etag=version)

    def getContainerSchedulingInfo(self, containerId):
        """Get scheduling information of a Concatenation inside a Group or TimeLink

        api: GET /containers/{containerId}/schedule

        usage:
           ::

               containerInfo, containerInfoVersion = api.getContainerSchedulingInfo(containerId)
        """
        return self.get('/containers/%d/schedule' % containerId)

    def saveContainerSchedulingInfo(self, containerId, containerInfo, version):
        """Update OB scheduling information.

        api: PUT /containers/%d/schedule

        usage:
           ::

               containerInfo, containerInfoVersion = api.getContainerSchedulingInfo(containerId)
               # change something
               containerInfo['groupContribution'] = 50
               api.saveContainerSchedulingInfo(containerId, containerInfo, containerInfoVersion)
        """
        return self.put('/containers/%d/schedule' % containerId, containerInfo, etag=version)

    def getContainerItemsSchedulingInfo(self, containerId):
        """Get scheduling information of all items (OBs or containers) in a container

        api: GET /containers/{containerId}/items/schedule

        usage:
           ::

               containerInfo, containerInfoVersion = api.getContainerItemsSchedulingInfo(containerId)
        """
        return self.get('/containers/%d/items/scheduling' % containerId)

# ---------- VISITOR EXECUTION SEQUENCE APIs ----------
    def getExecutionSequence(self, instrument):
        """Retrieve the personal execution sequence for an instrument.

        api: GET /executionSequences/{instrument}

        usage:
           ::

              executionSequence, esVersion = api.getExecutionSequence('UVES')
        """
        return self.get('/executionSequences/%s' % instrument)

    def saveExecutionSequence(self, instrument, executionSequence, version):
        """Change personal visitor execution sequence for an instrument.

        The list should contain objects with an obId in the desired execution
        order and may also contain OBs from delegated observing runs. Only
        visitor mode OBs in status '+', 'A', 'X' or 'S' can be included.

        The obId is the only required field in each list member, but all fields
        sent by a GET request can be included unchanged.

        api: PUT /executionSequences/{instrument}

        usage:
           ::

              executionSequence, esVersion = api.getExecutionSequence('UVES')
              executionSequence, esVersion = api.saveExecutionSequence('UVES',
                 [{ 'obId': ob1 }, { 'obId': ob2 }], esVersion)
              print('OBs in UVES execution sequence', ', '.join(str(e['obId']) for e in executionSequence))
        """
        return self.put('/executionSequences/%s' % instrument, executionSequence, version)

# ---------- INSTRUMENT PACKAGE APIs ----------
    def getInstrumentConstraints(self, instrument, ipVersion):
        """Get all observing constraints that OBs using this instrument package
        must define.

        The information returned is useful for building a user interface and
        also contains allowed values or ranges.

        api: GET /instrumentPackages/{instrument}/{ipVersion}/instrumentConstraints

        usage:
           ::

              insConstraints, _ = api.getInstrumentConstraints('UVES', '98.09')
        """
        return self.get('/instrumentPackages/%s/%s/instrumentConstraints' % (instrument, ipVersion))

    def getTemplateSignatures(self, instrument, ipVersion, phase='phase2' ):
        """List all template signatures that can be attached to OBs using this
        instrument package.

        api: GET /instrumentPackages/{instrument}/{ipVersion}/templateSignatures

        usage:
           ::

              tplSignatures, _ = api.getTemplateSignatures('UVES', '98.09')
              tplSignatures, _ = api.getTemplateSignatures('UVES', '98.09', 'phase1')
              tplSignatures, _ = api.getTemplateSignatures('UVES', '98.09', 'phase2')
        """
        assert phase in ['phase1','phase2']
        return self.get('/instrumentPackages/%s/%s/templateSignatures?for=%s' % (instrument, ipVersion, phase))

    def getTemplateSignature(self, instrument, ipVersion, templateName):
        """Get a specific template signature.

        api: GET /instrumentPackages/{instrument}/{ipVersion}/templateSignatures/{templateName}

        usage:
           ::

              tplSignature, _ = api.getTemplateSignature('UVES', '98.08', 'UVES_blue_acq_slit')
        """
        return self.get('/instrumentPackages/%s/%s/templateSignatures/%s' % (instrument, ipVersion, templateName))

    def getInstrumentPackageVersions(self, instrument):
        """Get list of instrument package versions.

        api: GET /instrumentPackages/{instrument}

        usage:
           ::

              ipVersions, _ = api.getInstrumentPackageVersions('UVES')
        """
        return self.get('/instrumentPackages/%s/' % instrument)

# ---------- USER APIs ----------
    def getUser(self):
        """Get information about the logged-in user.

        api: GET /authenticatedUser

        usage:
           ::

              user, _ = api.getUser()
        """
        return self.get('/authenticatedUser')

# ---------- private methods ----------
#  Retry Handling for requests
# See https://www.peterbe.com/plog/best-practice-with-retries-with-requests
# Or https://findwork.dev/blog/advanced-usage-python-requests-timeouts-retries-hooks/
    def requests_retry_session(self):
        adapter = requests.adapters.HTTPAdapter(max_retries=3)
        session = requests.Session()
        session.mount('https://', adapter)
        return session

    def request(self, method, url, data=None, etag=None):
        self.request_count += 1

        # configure request headers
        assert self.access_token is not None
        headers = {
            'Authorization': 'Bearer ' + self.access_token,
            'Accept': 'application/json'
        }
        if data is not None:
            headers['Content-Type'] = 'application/json'
        if etag is not None:
            headers['If-Match'] = etag

        # make request
        url = self.apiUrl + url
        if self.debug:
            print(method, url, data)
        r = self.session.request(method, url, headers=headers, data=json.dumps(data))
        content_type = r.headers['Content-Type'].split(';')[0]
        etag = r.headers.get('ETag', None)

        # handle response
        if 200 <= r.status_code < 300:
            if content_type == 'application/json':
                data = r.json()
                return data, etag
            return None, etag
        elif content_type == 'application/json' and 'error' in r.json():
            raise P2Error(r.status_code, method, url, r.json()['error'])
        else:
            raise P2Error(r.status_code, method, url, 'oops unknown error')

    def uploadFile(self, method, url, filename, contentType, etag=None):
        basename = os.path.basename(filename)
        assert self.access_token is not None
        headers = {
            'Authorization': 'Bearer ' + self.access_token,
            'Content-Disposition': 'inline; filename="%s"' % basename,
            'Content-Type': contentType
        }
        if etag is not None:
            headers['If-Match'] = etag
        with open(filename, 'rb') as f:
            r = self.session.request(method, self.apiUrl + url, data=f, headers=headers)
            if r.status_code == 201 or r.status_code == 204:
                etag = r.headers.get('ETag', None)
                return basename, etag
            else:
                content_type = r.headers['Content-Type'].split(';')[0]
                if content_type == 'application/json' and 'error' in r.json():
                    raise P2Error(r.status_code, method, url, r.json()['error'])
                else:
                    raise P2Error(r.status_code, method, url, 'oops unknown error')

    def downloadTextFile(self, url, filename):
        assert self.access_token is not None
        headers = {
            'Authorization': 'Bearer ' + self.access_token,
            'Accept': 'text/plain'
        }
        r = self.session.request('GET', self.apiUrl + url, stream=True, headers=headers)
        with open(filename, 'wb') as f:
            for line in r.iter_lines():
                f.write(line + b'\n')
        return None, r.headers.get('ETag', None)

    def downloadBinaryFile(self, url, filename):
        assert self.access_token is not None
        headers = {
            'Authorization': 'Bearer ' + self.access_token
        }
        r = self.session.request('GET', self.apiUrl + url, stream=True, headers=headers)
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=128):
                f.write(chunk)
        return None, None

    def get(self, url):
        return self.request('GET', url)

    def put(self, url, data, etag=None):
        return self.request('PUT', url, data, etag)

    def post(self, url, data=None, etag=None):
        return self.request('POST', url, data, etag)

    def delete(self, url, etag=None):
        return self.request('DELETE', url, etag=etag)
