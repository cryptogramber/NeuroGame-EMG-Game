#!/usr/bin/env python
# gameSession.py 

import wx, wave, math, os, sys
import cPickle as pickle
from StringIO import StringIO
from array import array
import time, datetime, paramiko
import secureConnectionHandler as ng_ssh

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~ 
class gameSession:
    def __init__(self):
        self.started = False
        self.EMGdata = [array('B'), array('B')]
        self.gameName = ''
        self.mouseGain = 0
        self.mousePow = 0
        self.subjectNum = 0
        self.localFilesDir = 'C:\\Neurogame' 

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~ 
    def Start(self, subjectNum, gameName, mouseGain, mousePow, sampleRate):
        if self.started:
            self.Stop()

        self.startTime = datetime.datetime.now()
        self.subjectNum = subjectNum
        self.EMGdata = [array('B'), array('B')]
        self.gameName = gameName
        self.mouseGain = mouseGain
        self.mousePow = mousePow
        self.sampleRate = sampleRate
        self.started = True

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~         
    def Append_EMG_String(self, datastr, channel):          # Add EMG data to data buffer, input is string
        self.EMGdata[channel].fromstring(datastr)

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~ 
    def Append_EMG_Bytearray(self, bytedata, channel):      # Add EMG data to data buffer, input is string
        self.EMGdata[channel] += bytedata

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~ 
    def Stop(self):                                         # Stop recording
        self.stoptime = datetime.datetime.now()
        self.started = False

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~ 
    def saveDataLocally(self,chA5xGain,chAGain,chAPGA,chB5xGain,chBGain,chBPGA):        # Save EMG data as a .wav file
        if self.started:
            self.Stop()
            
        numSamples = min([len(self.EMGdata[0]), len(self.EMGdata[1])])
        numChannels = len(self.EMGdata)

        if not numSamples or not numChannels:
            return

        self.basePath = self.localFilesDir +  '\\Subject_' + str(self.subjectNum)
        if not os.path.exists(self.basePath):
            os.makedirs(self.basePath)

        localFilesDir = self.basePath + '\\Subject_' + str(self.subjectNum) + '_Gameplay_' + self.startTime.strftime('%y%m%d_%H%M%S')
        w = wave.open( localFilesDir + '.wav', "w" )
        w.setnchannels( len(self.EMGdata) )
        w.setsampwidth( 1 ) #BYTES
        w.setframerate( self.sampleRate )
        data = array( 'B' )
        
        print "Saving game bout data to file: " + localFilesDir 
        print "saving EMG wave data: numsamps=" + str(numSamples) + " numchans=" + str(numChannels)

        for frame in xrange( numSamples ):
            for chan in xrange(numChannels):
               data.append( self.EMGdata[chan][frame])

        td = self.stoptime - self.startTime
        w.writeframes( data ) 
        w.close()
        textfile = open(localFilesDir + '.txt', "w")
        textfile.write("{\n")
        textfile.write("\"userid\":\"%d\",\n" % int(self.subjectNum))
        # Neurochip Gain values - with header then data on new line
        textfile.write("\"ch_a_5x_gain\":\"%f\",\n" % chA5xGain)
        textfile.write("\"ch_a_filter_gain\":\"%f\",\n" % chAGain)
        textfile.write("\"ch_a_pga_index\":\"%f\",\n" % chAPGA)
        textfile.write("\"ch_b_5x_gain\":\"%f\",\n" % chB5xGain)
        textfile.write("\"ch_b_filter_gain\":\"%f\",\n" % chBGain)
        textfile.write("\"ch_b_pga_index\":\"%f\",\n" % chBPGA)
        textfile.write("\"game_name\":\"%s\",\n" % self.gameName)
        textfile.write("\"mouse_gain\":\"%f\",\n" % self.mouseGain)
        textfile.write("\"mouse_power\":\"%f\",\n" % self.mousePow)
        textfile.write("\"start_time\":\"%s\",\n" % self.startTime.strftime('%Y/%m/%d %H:%M:%S'))
        textfile.write("\"duration_in_seconds\":\"%d\"\n" % td.seconds)
        textfile.write("}")
        textfile.close()

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~ 
    def secureServerUpload(self, subjectNum, serverHost, serverDir, serverLogin):
        # get a list of the files in the local data file folder
        self.subjectNum = subjectNum
        localFilesDir = self.localFilesDir + '\\Subject_' + str(self.subjectNum) 
        dirlist = os.listdir(localFilesDir)

        # extract the text and wav files from the list
        localFileList = [e for e in dirlist if e.endswith(".txt")]
        localFileList += [e for e in dirlist if e.endswith(".wav")]
        localFileList += [e for e in dirlist if e.endswith(".pkl")]

        # exit if no data files to upload
        if not len(localFileList):
            print "There are no new data files to upload."
            return
           
        # connect to secure server
        #secureConnection = ng_ssh.connect('hostname', 'username', 'id_rsa')
        try:
            secureConnection = ng_ssh.connect(serverHost, serverLogin, 'id_rsa')
            ng_ssh.exec_cmd(secureConnection, 'a')
            ng_ssh.exec_cmd(secureConnection, 's')
            checkServerDir = ng_ssh.exec_cmd(secureConnection, "[ -d " + str(serverDir) + " ] && echo exists || echo DNE")
            stringServerDir = str(checkServerDir[0]).strip()
            if stringServerDir == "DNE":
                ng_ssh.exec_cmd(secureConnection, "mkdir " + str(serverDir))
                print "Server base file directory not found: creating it now."
            elif stringServerDir == "exists":
                print "Server base file directory located."
            else:
                print "Error checking for base file directory."
                return
            serverFilesDir = serverDir + '/Subject_' + str(self.subjectNum)
            checkFilesDir = ng_ssh.exec_cmd(secureConnection, "[ -d " + str(serverFilesDir) + " ] && echo exists || echo DNE")
            stringFilesDir = str(checkFilesDir[0]).strip()
            if stringFilesDir == "DNE":
                ng_ssh.exec_cmd(secureConnection, "mkdir " + str(serverFilesDir))
                print "Subject file directory not found: creating it now."
            elif stringFilesDir == "exists":
                print "Subject file directory located."
            else:
                print "Error checking for subject file directory."
                return

            serverFileList = ng_ssh.exec_cmd(secureConnection, "cd " + str(serverFilesDir) + " && ls")
            serverFileList = [filename.rstrip("\n") for filename in serverFileList]
            serverFileList = [filename.strip() for filename in serverFileList]
            remoteFileList = [filename for filename in serverFileList if filename.endswith(".txt")]
            remoteFileList += [filename for filename in serverFileList if filename.endswith(".wav")]
            remoteFileList += [filename for filename in serverFileList if filename.endswith(".pkl")]

            sftpConnection = ng_ssh.sftp_connect(secureConnection)
            fileDifferences = []            # start with an empty list
            for x in localFileList:
                if not x in remoteFileList:
                    localFile = localFilesDir + "\\" + x
                    remoteFile = serverFilesDir + "/" + x
                    sftpConnection.put(localFile, remoteFile)
                    print "Uploaded " + str(localFile) + " to " + str(remoteFile)

        except:
            print "Could not connect -- check internet connection."
            return
