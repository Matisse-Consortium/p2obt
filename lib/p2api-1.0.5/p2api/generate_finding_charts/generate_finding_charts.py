#! /usr/bin/env python

# $Id: generate_finding_charts.py 267033 2021-09-16 11:08:57Z jpritcha $
from __future__ import print_function

_VERSION_ = "$Revision: 267033 $"

import sys                            # interaction with Python interpreter
import os, os.path                    # operating system services
from optparse import OptionParser     # for parsing command line arguments
from optparse import OptionGroup
import optparse
#from optparse import HelpFormatter 

import logging

import getpass
import keyring
import datetime
import time
import warnings
import json
import requests

import p2api

################################################################################

# ---------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------
def get_attrs(klass):
  return [k for k in klass.__dict__.keys()
    if not k.startswith('__')
    and not k.endswith('__')]

# ---------------------------------------------------------------------------------------
# https://gist.github.com/cynici/4084518
'''
optparse offers IndentedHelpFormatter() and TitledHelpFormatter() but they don't honor the newlines embedded in the description string.
author: Tim Chase
source: https://groups.google.com/forum/?fromgroups=#!topic/comp.lang.python/bfbmtUGhW8I
usage: parser = OptionParser(description=help_text, formatter=IndentedHelpFormatterWithNL())
'''

from optparse import OptionParser, IndentedHelpFormatter, textwrap

class IndentedHelpFormatterWithNL(IndentedHelpFormatter):
  def format_description(self, description):
    if not description: return ""
    desc_width = self.width - self.current_indent
    indent = " "*self.current_indent
# the above is still the same
    bits = description.split('\n')
    formatted_bits = [
      textwrap.fill(bit,
        desc_width,
        initial_indent=indent,
        subsequent_indent=indent)
      for bit in bits]
    result = "\n".join(formatted_bits) + "\n"
    return result

  def format_option(self, option):
    # The help for each option consists of two parts:
    #   * the opt strings and metavars
    #   eg. ("-x", or "-fFILENAME, --file=FILENAME")
    #   * the user-supplied help string
    #   eg. ("turn on expert mode", "read data from FILENAME")
    #
    # If possible, we write both of these on the same line:
    #   -x    turn on expert mode
    #
    # But if the opt string list is too long, we put the help
    # string on a second line, indented to the same column it would
    # start in if it fit on the first line.
    #   -fFILENAME, --file=FILENAME
    #       read data from FILENAME
    result = []
    opts = self.option_strings[option]
    opt_width = self.help_position - self.current_indent - 2
    if len(opts) > opt_width:
      opts = "%*s%s\n" % (self.current_indent, "", opts)
      indent_first = self.help_position
    else: # start help on same line as opts
      opts = "%*s%-*s  " % (self.current_indent, "", opt_width, opts)
      indent_first = 0
    result.append(opts)
    if option.help:
      help_text = self.expand_default(option)
# Everything is the same up through here
      help_lines = []
      for para in help_text.split("\n"):
        help_lines.extend(textwrap.wrap(para, self.help_width))
# Everything is the same after here
      result.append("%*s%s\n" % (
        indent_first, "", help_lines[0]))
      result.extend(["%*s%s\n" % (self.help_position, "", line)
        for line in help_lines[1:]])
    elif opts[-1] != "\n":
      result.append("\n")
    return "".join(result)
################################################################################
class get_options:
  "get command line options"

  def __init__(self, vers="0.0"):
    # define options and arguments
    parser = OptionParser(version="%prog "+vers, formatter=IndentedHelpFormatterWithNL())

    group = OptionGroup(parser, "Input OB(s)")
    group.add_option("-i", "--ids", dest="ids", metavar="Ids", help="List of OB IDs [required]", default=None)
    group.add_option("--obsdate", dest="obsdate", metavar="OBS_DATE", help="Set the obsdate [optional]", default=None)
    parser.add_option_group(group)

    group = OptionGroup(parser, "Image display parameters",
"""\
The following parameters affect the way the 'default' images are displayed in the FCs.
They correspond directly to the corresponding parameters of the APLPY FITSFigure.show_grayscale method, see:
  https://aplpy.readthedocs.io/en/stable/api/aplpy.FITSFigure.html#aplpy.FITSFigure.show_grayscale
for details.
"""
    )
    group.add_option("--pmax", dest="pmax", metavar="PMAX", help="pmax to apply to the display of first FC [optional]", type='float', default=None)
    group.add_option("--pmin", dest="pmin", metavar="PMIN", help="pmin to apply to the display of first FC [optional]", type='float', default=None)
    group.add_option("--stretch", dest="stretch", metavar="STRETCH", help="Stretch to apply to the display of first FC [optional]\n", default=None)
    group.add_option("--exponent", dest="exponent", metavar="EXPONENT", help="Exponent if stretch='power' [optional]\n", default=None)
    parser.add_option_group(group)

    group = OptionGroup(parser, "Custom Image/Survey",
"""\
The following parameters affect the way the 'default' images are displayed in the FCs.
They correspond directly to the corresponding parameters without 'c_' prefixes of the APLPY FITSFigure.show_grayscale method, see:
  https://aplpy.readthedocs.io/en/stable/api/aplpy.FITSFigure.html#aplpy.FITSFigure.show_grayscale
for details.
"""
    )
    group.add_option("--survey", dest="survey", metavar="SURVEY", help="An alternative SkyView survey to use. Use --supported_surveys to see which surveys are supported. [optional]", default=None)
    group.add_option("--bkg_image", dest="bkg_image", metavar="BK_IMAGE", help="A custom background image to use [optional]", default=None)
    group.add_option("--bkg_lam", dest="bkg_lam", metavar="BK_LAM", help="Description of the WL coverage of the custom background image/survey [optional]", default=None)
    group.add_option("--c_pmax", dest="c_pmax", metavar="PMAX", help="pmax to apply to the display of first FC [optional]", type='float', default=None)
    group.add_option("--c_pmin", dest="c_pmin", metavar="PMIN", help="pmin to apply to the display of first FC [optional]", type='float', default=None)
    group.add_option("--c_stretch", dest="c_stretch", metavar="STRETCH", help="Stretch to apply to the display of first FC [optional]\n", default=None)
    group.add_option("--c_exponent", dest="c_exponent", metavar="EXPONENT", help="Exponent if stretch='power' [optional]\n", default=None)
    parser.add_option_group(group)

    group = OptionGroup(parser, "Gaia pseudo images parameters",
        "The following parameters affect the way the Gaia pseudo images (if any) are constructed."
    )
    group.add_option("--GAIA_im_IQ", dest="GAIA_im_IQ", metavar="FWHM",
        help="FWHM to use for any Gaia images that will be generated [optional]",
        type='float',
        default=None
    )
    group.add_option("--GAIA_im_noise", dest="GAIA_im_noise", metavar="NOISE",
        help=
"""\
GAIA_im_noise is a dimensionless factor, with the noise computed via the numpy method random.normal(loc,scale) with loc=0.0 and:
    scale=GAIA_im_noise*<brightest_flux_value>
with <brightest_flux_value> being the maximum pixel value in the noiseless pseudo image.
The default value is (as at 2020-01): 1e-6
Together with pmin and pmax this parameter gives (some) control over the relative appearance of stars of different brightness, and can thus be helpful to (for example) highlight faint, but not insignificant, field star(s).
[optional] default=1e-6
""",
        type='float', default=None
    )
    group.add_option("--c_GAIA_im_IQ", dest="c_GAIA_im_IQ", metavar="FWHM",
        help="Same as --GAIA_im_IQ but for any Gaia pseudo images associated with the custom FC.",
        type='float',
        default=None
    )
    group.add_option("--c_GAIA_im_noise", dest="c_GAIA_im_noise", metavar="NOISE",
        help="Same as --GAIA_im_noise but for any Gaia pseudo images associated with the custom FC.",
        type='float',
        default=None
    )
    parser.add_option_group(group)

    group = OptionGroup(parser, "p2 server selection, options and password management")
    group.add_option("--env", dest="env", help="Use the %s environment [optional], default = production" %("|".join(p2api.API_URL.keys())), default='production')
    group.add_option("-u", "--user", dest="user", metavar="USER", help="the User Portal account of the user to use, e.g. ASMITHSONIAN [required for production (not required for demo)]", default=None)
    group.add_option("-S", "--PWstore", dest="pwstore", metavar="PWSTORE", help="Store the password in the keyring, default=False", action="store_true", default=False)
    group.add_option("-R", "--PWreenter", dest="pwreenter", metavar="PWREENTER", help="Reenter the password, thus overriding any PW in the keyring, default=False", action="store_true", default=False)
    group.add_option("-Z", "--PWremove", dest="pwremove", metavar="PWREMOVE", help="Remove any password from the keyring, default=False", action="store_true", default=False)
    parser.add_option_group(group)

    group = OptionGroup(parser, "help...")
    group.add_option("--supported_surveys", dest="supSurs", metavar="Ids", help="Report the list of supported surveys",  action="store_true", default=False)
    parser.add_option_group(group)

    group = OptionGroup(parser, "Verbosity...",
                    "All optional")
    group.add_option("-D", "--debug", dest="debug", help="Write out debugging info [optional]", action="store_true", default=False)
    group.add_option("-v", "--verbose", dest="vbose", help="Write out verbose info [optional]", action="store_true", default=False)
    group.add_option("-q", "--quiet", dest="quiet", help="Write out minimal info [optional]", action="store_true", default=False)
    parser.add_option_group(group)

    # parse arguments
    (options, args) = parser.parse_args()

    if not options.ids and not options.supSurs :
        parser.print_help()
        sys.exit(2)

    self.ids = options.ids
    self.obsdate = options.obsdate

    self.pmin = options.pmin
    self.pmax = options.pmax
    self.stretch = options.stretch
    self.exponent = options.exponent
    self.GAIA_im_IQ = options.GAIA_im_IQ
    self.GAIA_im_noise = options.GAIA_im_noise

    self.survey = options.survey
    self.bkg_image = options.bkg_image
    self.bkg_lam = options.bkg_lam
    self.c_pmin = options.c_pmin
    self.c_pmax = options.c_pmax
    self.c_stretch = options.c_stretch
    self.c_exponent = options.c_exponent
    self.c_GAIA_im_IQ = options.c_GAIA_im_IQ
    self.c_GAIA_im_noise = options.c_GAIA_im_noise

    self.user = options.user
    self.env = options.env
    self.pwstore = options.pwstore
    self.pwreenter = options.pwreenter
    self.pwremove = options.pwremove

    self.supSurs = options.supSurs

    self.debug = options.debug
    self.vbose = options.vbose
    self.quiet = options.quiet

    logFMT = "%(asctime)s %(module)15s[%(process)5d] [%(levelname)s] %(message)s"
    logLVL=logging.INFO
    if options.vbose:
      logLVL=logging.INFO
    if options.debug:
      logLVL=logging.DEBUG
    if options.quiet:
      logLVL=logging.WARN
    logging.basicConfig(level=logLVL, format=logFMT)

options = get_options(_VERSION_)

################################################################################
def rgetFolderIds( api, cIds ):

    ids = []
    for cId in cIds :
        rItems, _ = api.get('/containers/'+str(cId)+'/items')
        logging.debug(rItems)
        for r in rItems :
            if r['itemType'] == 'Folder' :
                logging.debug('Adding %d to folder list' %(r['containerId']))
                ids.extend([r['containerId'],])
                ids.extend(rgetFolderIds(api, [r['containerId'],]))
    return ids
################################################################################
def rgetContainerIds( api, cIds, status=None ):
    ids = []
    for cId in cIds :
        rItems, _ = api.get('/containers/'+str(cId)+'/items')
        logging.debug(rItems)
        for r in rItems :
            if r['itemType'] == 'TimeLink' or r['itemType'] == 'Group' or r['itemType'] == 'Concatenation' :
                if status is None or r['containerStatus'] in list(status) :
                    logging.debug('Adding %d to container list' %(r['containerId']))
                    ids.extend([r['containerId'],])
    return ids

################################################################################
def rgetOBIds( api, cIds, status=None ):
    ids = []
    for cId in cIds :
        logging.debug('Checking container %d' %(cId))
        rItems, _ = api.get('/containers/'+str(cId)+'/items')
        logging.debug(rItems)
        for r in rItems :
            if r['itemType'] == 'OB' or  r['itemType'] == 'CB' :
                if status is None or r['obStatus'] in list(status) :
                    logging.debug('Adding %d to OB list' %(r['obId']))
                    ids.extend([r['obId'],])
    return ids

################################################################################
# ------------------------------------------------------------------------------
def oneOB( api, obId ) :
    try :
        OB, _  = api.getOB(obId)
    except p2api.P2Error as e :
        ## Looks like this ID is not an OB...
        logging.error('OB %d could not be found...' %(obId))
        return
    except:
        raise
    
    if OB['itemType'] not in ['OB',] :
        logging.warning('OB %d is not a science OB' %(obId))
        return

    if OB['obStatus'] not in ['P','-'] :
        logging.warning('OB status is %s, OB not modifiable' %(OB['obstatus']))
        return

    runId, _ = api.getRun(OB['runId'])
    ob_url=api.apiUrl+'/obsBlocks/'+str(obId)
    oneOB_sdt=datetime.datetime.now()
    logging.info("Creating finding charts for OBid = %d, OBname = '%s' @ %s..." % (OB['obId'],OB['name'],OB['instrument']))
    data = api.generateFindingChart(
        obId,
        obs_date=options.obsdate,
        stretch=options.stretch,
        exponent=options.exponent,
        pmin=options.pmin,
        pmax=options.pmax,
        GAIA_im_IQ=options.GAIA_im_IQ,
        GAIA_im_noise=options.GAIA_im_noise,
        survey=options.survey,
        bkg_image=options.bkg_image,
        bkg_lam=options.bkg_lam,
        c_stretch=options.c_stretch,
        c_exponent=options.c_exponent,
        c_pmin=options.c_pmin,
        c_pmax=options.c_pmax,
        c_GAIA_im_IQ=options.c_GAIA_im_IQ,
        c_GAIA_im_noise=options.c_GAIA_im_noise,
    )
    oneOB_edt=datetime.datetime.now()
    logging.info("Finding chart for OBid = %d, OBname = '%s' @ %s done in %s." % (obId, OB['name'], OB['instrument'], str(oneOB_edt-oneOB_sdt)))
    if data is not None :
        try :
            jwarn=json.loads(r.content.decode('utf-8'))
            if 'warnings' in jwarn.keys() :
                logging.warning(jwarn['warnings'])
        except :
            pass
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------

def main():

    ################################################################################
    # remove passowrd from keyring...
    if options.pwremove and options.user is not None :
        keyring.delete_password('usd_p2api_interactive:www.eso.org', options.user)
        sys.exit(0)
    
    ################################################################################
    if options.supSurs :
        r = requests.get('%s/supported_surveys' %(p2api.P2FC_URL[options.env]))
        if r.status_code in [200,201,204] :
            print(r.text)
        else:
            raise(r.text)
        sys.exit(0)

    password_from_keyring = None
    # Login...
    if options.env in ['demo',]:
        user='52052'
        pwstream='tutorial'
    else:
        user=options.user
        ## from astroquery.eso
        # Get password from keyring or prompt
        if options.pwreenter is False:
            password_from_keyring = keyring.get_password(
                "usd_p2api_interactive:www.eso.org", user)

        if password_from_keyring is None:
            #if system_tools.in_ipynb():
            #    log.warning("You may be using an ipython notebook:"
            #                " the password form will appear in your terminal.")
            # see https://pymotw.com/2/getpass/
            if sys.stdin.isatty():
                pwstream = getpass.getpass(user+"@<"+options.env+"> password : ", stream=sys.stderr)
            else:
                pwstream = sys.stdin.readline().rstrip()
        else:
            pwstream = password_from_keyring

    #login to the API
    i=0
    api = None
    while api is None and i < 10 :
        try:
            api = p2api.ApiConnection(options.env, user, pwstream)
        except p2api.P2Error :
            logging.error(p2api.P2Error)
            time.sleep(2)
        except :
            pass
        i+=1
    if i == 10 :
        logging.error('Ooops, login failed...')
        sys.exit(1)
    
    ## from astroquery.eso
    # When authenticated, save password in keyring if needed
    if options.env not in ['demo','defidev7',] and password_from_keyring is None and options.pwstore:
        keyring.set_password("usd_p2api_interactive:www.eso.org", user, pwstream)

    obIds=[]
    for ID in options.ids.split(',') :
        nID=int(ID)
        logging.info("Processing OB/Container ID = %d" %(nID))
        # The containes and OBs
        try:
            container, containerVersion = api.getContainer(nID)
            fIds = [nID,]
            fIds.extend(rgetFolderIds(api, [nID,]))
            logging.info('================================================================================')
            cIds=rgetContainerIds(api, fIds )
            fcIds = fIds+cIds
            if cIds is not None :
                logging.info("containerId list = %s" %(str(cIds)))
            else :
                logging.error("No containers found")
            logging.info('================================================================================')
            obIds=obIds+rgetOBIds(api, fcIds )
            logging.info("obId list = %s" %(str(obIds)))
            if obIds is None :
                logging.error("No OBs found")

        except p2api.P2Error as e :
            ## Looks like this ID is not a container, assume it is an OB, below...
            obIds.append(nID)
        except:
            raise

    if len(obIds) > 0 :
        if len(obIds) > 1 :
            sdt=datetime.datetime.now()
            logging.warning('Submitting %d OBs for FC generation...' %( len(obIds) ))
        for obId in obIds :
            oneOB(api, obId)
        if len(obIds) > 1 :
            edt=datetime.datetime.now()
            logging.info('Total elapsed time to process %d finding charts %s...' %(len(obIds),str(edt-sdt)))
    else :
        logging.error('No OBs found.')

if __name__ == '__main__' :
    main()
