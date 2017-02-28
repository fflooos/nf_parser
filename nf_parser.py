#!/usr/bin/env python

import csv
import os
import logging
from optparse import OptionParser

# Get script current directory
scriptDir = os.path.dirname(os.path.abspath(__file__))


# Parse command line arguments
parser = OptionParser()
parser.add_option("-o", "--output", dest="outfile",
                  help="Specify output file name, default name: autolink.csv", metavar="FILE", default="autolink.csv")
parser.add_option("-d", "--directory", dest="reportPath",
                  help="Specify Network Ferret /report path")
parser.add_option("-v", "--verbose",
                  action="store_true", dest="debug", default=False,
                  help="Enable debug mode")

(options, args) = parser.parse_args()

#Initiate logger
logging.basicConfig(filename='nf_parser.log', format='%(asctime)s %(levelname)s:%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
logging.info('Starting adhoc_generator...')

global debug

def parse_router(fileIn):

    rt_dic = {}
    with open(fileIn) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        logging.info('Parsing '+fileIn+' file...')
        cmt_regex = ['^#.*', '^\ *$', '^\*', '^\*+']

        linecount = 1

        for row in readCSV:
            if len(row) == 0 or linecount == 1:
                linecount +=1
                continue

            if row[0] in rt_dic:
                tmp_l = rt_dic[row[0]]
                if row[6] in tmp_l:
                    logging.error('Duplicated interface for device: '+row[0])
                else:
                    tmp_l[row[6]] = row[3]

                rt_dic[row[0]] = tmp_l
            else:
                if_dic = dict()
                if_dic[row[6]] = row[3]
                rt_dic[row[0]] = if_dic
            linecount += 1

    return rt_dic

def parse_result(fileIn):

    rt_dic = {}
    with open(fileIn) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        logging.info('Parsing '+fileIn+' file...')
        cmt_regex = ['^#.*', '^\ *$', '^\*', '^\*+']

        linecount = 1
        for row in readCSV:
            if len(row) == 0 or linecount == 1:
                linecount +=1
                continue

            src_ip = row[1]
            conn_type = row[2]

            if src_ip in rt_dic:
                tmp_l = rt_dic[src_ip]
                if conn_type in tmp_l:
                    tmp_sublist = tmp_l[conn_type]
                    res = _parse_row(row[2], row[4], os.path.basename(fileIn))
                    if res != 0 :
                        tmp_sublist[ len(tmp_sublist) ] = res
                else:
                    logging.info('New connection type: '+row[2]+'found for device: '+row[1])
                    tmp_sublist = dict()
                    res = _parse_row(row[2], row[4], os.path.basename(fileIn))
                    if res != 0:
                        tmp_sublist[0] = res
                    tmp_l[conn_type] = tmp_sublist

                rt_dic[src_ip] = tmp_l
            else:
                tmp_sublist = dict()
                res = _parse_row(row[2], row[4], os.path.basename(fileIn))
                if res != 0:
                    tmp_sublist[0] = res
                tmp_l = dict()
                tmp_l[conn_type] = tmp_sublist
                rt_dic[src_ip] = tmp_l
            linecount += 1

    return rt_dic

def _sel_mapping(row_type, row, file_name):

    #print row_type, row, file_name
    l3_mapping_list = {
        "Interface": { 'snmpIndex':0, 'remoteIndex': 1, 'connectionId':3, 'remoteAddr':5},
        "LDPPeer": {  'snmpIndex':0, 'localLS':3, 'remoteLS': 4, 'connectionId':5},
        "BGPPeer": { 'connectionId':2, 'remotePort':3, 'remoteBGPAddress': 6, 'snmpIndex':9},
        "ISISAdjacency": { 'snmpIndex':0, 'remoteRouterId':2, 'ifIndex': 5},
    }
    l2_mapping_list = {
        "l2_map1": {'snmpIndex': 0, 'remoteIndex': 1, 'remoteAddr': 4},
        "l2_map2": {'snmpIndex': 0, 'remoteIndex': 1, 'remoteAddr': 4},
    }
    connectivity_raw = {
        "m1": {'snmpIndex': 0, 'unknownConnection': 1, 'connectionId':2, 'connectionType': 3},
        "m2": {'snmpIndex': 0, 'remoteSnmpIndex': 1, 'remoteSysName': 2, 'connectionId': 3, 'connectionType': 4, 'remoteAddress': 5},
    }

    if file_name == "layer3_raw.csv":
        for k, v in l3_mapping_list.items():
            if row_type == k : return l3_mapping_list[k]
    elif file_name == "layer2_raw.csv":
        for k, v in l2_mapping_list.items():
            if row_type == k : return l2_mapping_list[k]
    elif file_name == "connectivity_raw.csv":
        for k, v in connectivity_raw.items():
            #print row[1]
            try:
                #TODO remove hardcoded column number row[1]
                value = row[1].split('=')
                if connectivity_raw[k].has_key(value[0]):
                    return connectivity_raw[k]
            except IndexError:
                logging.error("Column out of range in connectivity_raw, please review mapping configuration")
    return 0




def _parse_row(row_type, row, fileType):
    if_line = row.split("  ")

    mapping = _sel_mapping(row_type, if_line, fileType)
    if debug: logging.debug("Mapping selected:"+mapping)
    if mapping != 0:
        result = dict()

        for k, v in mapping.items():
            try :
                value = if_line[mapping[k]].split('=')
                result[k] = value[1]
            except IndexError:
                logging.error("Column out of range - Wrong mapping please review mapping")
                logging.error("Current mapping:"+mapping)

        return result
    return 0

# MAIN
if __name__ == '__main__':

    # Enable debug if option -v is specified
    if ( options.debug ) : debug = True
    else : debug = False

    #checkoptions(options)
    logging.info('Starting parser...')

    for root, dirs, files in os.walk(options.reportPath):
        for basename in files :
                # Discard not .csv files
                if basename.endswith(".csv"):
                    #print basename
                    if basename == "routerPorts.csv":
                        rt_ref = parse_router(os.path.join(root, basename))
                    elif basename == "layer3_raw.csv":
                        l3_ref = parse_result(os.path.join(root, basename))
                    elif basename == "connectivity_raw.csv":
                        conn_ref = parse_result(os.path.join(root, basename))

    out_dict = dict()

    print "############### ROUTER PORT MAPPING ###############"
    for k, v in rt_ref.items():
        print "key:", k, "value:", v


    print "############### L3 MAPPING ###############"
    for k, v in l3_ref.items():
        #print "key:", k, "value:", v
        for sk, sv in l3_ref[k].items():
            for ssk, ssv in l3_ref[k].get(sk).items():
                if ssv.has_key('remoteBGPAddress'):
                    #print ssv
                    pass
                    #split_v = ssv.get('unknownConnection').split(':')
                    #print sk, k, rt_ref[k].get(ssv.get('snmpIndex')), ssv.get('connectionType'), split_v[0], split_v[1]
                elif ssv.has_key('remoteLS'):
                    pass
                    #print sk, k, rt_ref[k].get(ssv.get('snmpIndex')), ssv.get('connectionType'), ssv.get('remoteAddress'), rt_ref[ssv.get('remoteAddress')].get(ssv.get('remoteSnmpIndex'))
                elif ssv.has_key('remoteIndex'):
                    print sk, k+'_161', 'LAN_'+k+'_161_'+rt_ref[k].get(ssv.get('snmpIndex')), ssv.get('connectionType'), ssv.get('remoteAddr')+'_161', 'LAN_'+ssv.get('remoteAddr')+'_161_'+rt_ref[ssv.get('remoteAddr')].get(ssv.get('remoteIndex'))

    print "############### Connectivity_raw ###############"
    for k, v in conn_ref.items():
        #print "key:", k, "value:", v
        for sk, sv in conn_ref[k].items():
            for ssk, ssv in conn_ref[k].get(sk).items():
                if ssv.has_key('unknownConnection'):
                    #print ssv
                    split_v = ssv.get('unknownConnection').split(':')
                    print sk, k+'_161', 'LAN_'+k+'_161_'+rt_ref[k].get(ssv.get('snmpIndex')), ssv.get('connectionType'), str(split_v[0])+'_161', 'LAN_'+split_v[0]+'_161_'+str(split_v[1])
                else:
                    print sk, k+'_161', 'LAN_'+k+'_161_'+rt_ref[k].get(ssv.get('snmpIndex')), ssv.get('connectionType'), ssv.get('remoteAddress')+'_161', 'LAN_'+ssv.get('remoteAddress')+'_161_'+rt_ref[ssv.get('remoteAddress')].get(ssv.get('remoteSnmpIndex'))