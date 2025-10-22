def setAfRange(self, int):
        # AfRangeEnum { AfRangeNormal = 0, AfRangeMacro = 1, AfRangeFull = 2 }
        self.cam.controls.AfRange = int
        self.camvals.setValue('Af/AfRange', int)
    
def setAfSpeed(self, bool):
    # 	AfSpeedEnum { AfSpeedNormal = 0, AfSpeedFast = 1 }
    if bool == True:
        self.cam.controls.AfSpeed = 1
        self.camvals.setValue('Af/AfSpeed', 1)
    else:
        self.cam.controls.AfSpeed = 0
        self.camvals.setValue('Af/AfSpeed', 0)

def setAfMetering(self,bool):
    # 	AfMeteringEnum { AfMeteringAuto = 0, AfMeteringWindows = 1 }
    if bool == True:
        self.cam.controls.AfMetering = 1
        self.camvals.setValue('Af/AfMetering', 1)
    else:
        self.cam.controls.AfMetering = 0
        self.camvals.setValue('Af/AfMetering', 0)

def setAfMode(self):
    #' afManual, afContinuous, afAuto'
    #print(self.sender().objectName())
    """ AfModeEnum { AfModeManual = 0, AfModeAuto = 1, AfModeContinuous = 2 } """
    # https://libcamera.org/api-html/namespacelibcamera_1_1controls.html#a34be6a087cc3175b29d8c046bd8c10f4
    if self.sender().objectName() == "afManual":
        self.cam.controls.AfMode = 0 # controls.afModeEnum.Manual
        self.camvals.setValue('Af/AfMode', 0)
        self.afManual.setChecked(True)
        if self.cam.camera_controls['AfMode']:
            self.diopters.setEnabled(True)

    if self.sender().objectName() == "afContinuous":
        self.cam.controls.AfMode =  2 #controls.afModeEnum.Continuous
        self.camvals.setValue('Af/AfMode', 2)
        self.afContinuous.setChecked(True)
        self.diopters.setEnabled(False)

    if self.sender().objectName() == "afAuto":
        self.cam.controls.AfMode = 1 #controls.afModeEnum.Auto
        self.camvals.setValue('Af/AfMode', 1)
        self.afAuto.setChecked(True)
        self.diopters.setEnabled(False)

def afCycleDone(self,job):
    result = self.cam.wait(job)
    if result == True:
        self.printt("Autofocus completed succesfully")
    else:
        self.printt("Autofocus did not complete succesfully!")
