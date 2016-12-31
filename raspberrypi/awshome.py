#!/usr/bin/env python

import os
import json
import time
#import pi_switch
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import logging

'''
class OnOff:
    def __init__(self, name, onCode, offCode, rf, iot):
        self.name = name
        self.onCode = onCode
        self.offCode = offCode
        self.rf = rf

        self.shadow = iot.createShadowHandlerWithName(self.name, True)
        self.shadow.shadowRegisterDeltaCallback(self.newShadow)
        self.set(False)

    def set(self, state):
        code = self.onCode if state else self.offCode
        print('Turning %s %s using code %i' % (self.name, 'ON' if state else 'OFF', code))
        self.rf.sendDecimal(code, 24)
        self.shadow.shadowUpdate(json.dumps({
            'state': {
                'reported': {
                    'light': state
                    }
                }
            }
        ), None, 5)

    def newShadow(self, payload, responseStatus, token):
        newState = json.loads(payload)['state']['light']
        self.set(newState)
'''

class OnOffIR:
    def __init__(self, iotName, irName, onButton, iot):
        self.iotName = iotName
        self.irName = irName
        self.onButton = onButton

        self.shadow = iot.createShadowHandlerWithName(self.iotName, True)
        self.shadow.shadowUpdate(json.dumps({
            'state': {
                'reported': {
                    'thomas': False
                    }
                }
            }
        ), None, 5)
        self.shadow.shadowRegisterDeltaCallback(self.newShadow)
        #self.set(False)

    def set(self, state):

        if state:
            logger.info('Turning %s %s using code %s' % (self.iotName, 'ON', self.onButton))
            print('Turning %s %s using code %s' % (self.iotName, 'ON', self.onButton))
            os.system("irsend SEND_ONCE thomas " + self.onButton)
            logger.info('Thomas running')

        #     self.shadow.shadowUpdate(json.dumps({
        #         'state': {
        #             'reported': {
        #                 'thomas': state
        #                 }
        #             }
        #         }
        #     ), None, 5)
        
        # #time.sleep(1)
        #     self.shadow.shadowUpdate(json.dumps({
        #         'state': {
        #             'reported': {
        #                 'thomas': False
        #                 }
        #             }
        #         }
        #     ), None, 5)

    def newShadow(self, payload, responseStatus, token):
        newState = json.loads(payload)['state']['thomas']
        #print newState
        logger.info(newState)
        self.set(newState)

    def disconnect(self):
        self.shadow.shadowUnregisterDeltaCallback()

    def connectToShadow(self, iot):
        self.shadow = iot.createShadowHandlerWithName(self.iotName, True)
        self.shadow.shadowRegisterDeltaCallback(self.newShadow)

def createIoT():
    iot = AWSIoTMQTTShadowClient('AWSHome', useWebsocket=True)
    iot.configureEndpoint('', 443)
    iot.configureCredentials(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'VeriSign-Class 3-Public-Primary-Certification-Authority-G5.pem'))
    iot.configureConnectDisconnectTimeout(10)  # 10 sec
    iot.configureMQTTOperationTimeout(5)  # 5 sec
    iot.connect()
    return iot

'''
def createRF():
    rf = pi_switch.RCSwitchSender()
    rf.enableTransmit(0)
    rf.setPulseLength(194)
    return rf
'''

if __name__ == "__main__":
    
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler('/home/pi/AWShome/aws_debug.log')
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)

    logger.info('Starting')

    time.sleep(30)

    try:

        iot = createIoT()
        #rf = createRF()

        # Create your switches here, using the format:
        #   OnOff(<THING NAME>, <ON CODE>, <OFF CODE>, rf, iot)
        #
        # Example:
        #   OnOff('floor-lamp', 284099, 284108, rf, iot)
        #
        ir = OnOffIR('thomas', 'thomas', 'BTN_TRIGGER', iot)

        print('Listening...')
        logger.info('Listening...')

        counter = 0
        while True:
            print counter
            time.sleep(0.2)
            counter = counter + 0.2
            # 23 hours
            if counter > 82800:
                print('~23 hours passed. Disconnecting and reconnecting.')
                logger.info('~23 hours passed. Disconnecting and reconnecting.')
                ir.disconnect()
                iot.disconnect()
                iot.connect()
                ir.connectToShadow(iot)
                counter = 0


    except Exception as e: 
        print str(e)
        logger.info(str(e))

    
