; This work is licensed under a Creative Commons Attribution-NonCommercial 4.0 International License. This license allows reusers to copy and redistribute the material in any medium or format and remix, transform, and build upon the material, as long as attribution is given to the creator. The license allows for non-commercial use only, and otherwise maintains the same freedoms as the regular CC license.
; This software, "Auto RadReport," is provided as a prototype and for informational purposes only. It is not necessarily secure or accurate and is provided "as is" without warranty of any kind. Users should use this software at their own risk.
; We make no representations or warranties of any kind, express or implied, about the completeness, accuracy, reliability, suitability or availability with respect to the software or the information, products, services, or related graphics contained on the software for any purpose. Any reliance you place on such information is therefore strictly at your own risk.
; This software is not intended for use in medical diagnosis or treatment or in any activity where failure or inaccuracy of use might result in harm or loss. Users are advised that health treatment or diagnosis decisions should only be made by certified medical professionals.
; In no event will we be liable for any loss or damage including without limitation, indirect or consequential loss or damage, or any loss or damage whatsoever arising from loss of data or profits arising out of, or in connection with, the use of this software.
; By using this software, you agree to this disclaimer and assume all risks associated with its use. We encourage users to ensure they comply with local laws and regulations and to use the software ethically and responsibly.


#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey 000000000
;;#Warn  ; Recommended for catching common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.

SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

DetectHiddenWindows, On

#f1::
GetPowerscribeTextboxname()

; Make sure to structure the JSON data with the accession number
acc:=GetPowerscribeElementInfo("Accession:") ; Retrieve the accession number using a function
; Create a JSON string with the accession number
; In AHK, you escape double quotes by doubling them
json := "{""accession_number"":""" acc """}"
Url := "http://127.0.0.1:5000/download_study"

; Create the HTTP request and set headers
http := ComObjCreate("WinHttp.WinHttpRequest.5.1")
; Set timeouts (in milliseconds)
; The parameters are: ResolveTimeout, ConnectTimeout, SendTimeout, and ReceiveTimeout
http.SetTimeouts(5000, 5000, 10000, 1200000) ; For example, here it's set to 5 seconds for resolve, 5 seconds for connect, 10 seconds for send, and 30 seconds for receive

http.Open("POST", Url, false)
http.SetRequestHeader("Content-Type", "application/json")

; Send the request with the JSON body
http.Send(json)

; Optionally handle the response
response := http.ResponseText

; Set the clipboard to the response
Clipboard := response

; Wait for the clipboard to contain the data
ClipWait, 1

; Presuming you've already set the clipboard to the desired response text

; Activate the PowerScribe 360 | Reporting window
If WinExist("PowerScribe 360 | Reporting")
{
    WinActivate  ; Uses the last found window from WinExist
    Sleep, 500   ; Wait a bit for the window to activate, adjust the delay as needed

    ; Send Ctrl+End to go to the end of the document
    SendInput ^{End}

    Sleep, 500   ; Optional: Wait a bit to ensure the cursor has moved to the end

    ; Send Ctrl+V to paste
    SendInput ^v
}

;Functions in the toolbox already

;can get the control name by whatever text is in the control
GetPowerscribeControlbyText(Text){
WinGet, PowerscribeControls, ControlList, PowerScribe 360 | Reporting
Loop, Parse, PowerscribeControls, `n
{
	ControlGetText, TempControlText, %A_LoopField%, PowerScribe 360 | Reporting
	If(TempControlText = Text)
	{
		ControlName := A_LoopField
		Break
	}
}
Return ControlName
}


GetPowerscribeElementInfo(Element){
	OpenPowerscribeSidePanel()
	;GetPowerscribeControlbyText only returns the control name of the actual Element itself but not the corresponding value in the adjacent control
	;this function will return something like GE12345679 if Element is "MRN:"
	tempstr := StrSplit(GetPowerscribeControlbyText(Element), "_ad")
	;get the control name for the adjacent control
	nextcontrolnumber := tempstr[2] - 1
	;reassemable the control name
	nextcontrol := tempstr[1] . "_ad" . nextcontrolnumber
	Controlgettext, ElementInfo, %nextcontrol%, PowerScribe 360 | Reporting
	Return ElementInfo
}


;Function to make sure the right side panel is open for data extraction.
OpenPowerscribeSidePanel(){
	WinGet, MMX2, MinMax, PowerScribe 360 | Reporting
	If (MMX2 == -1)
		WinRestore, PowerScribe 360 | Reporting
	WinActivate, PowerScribe 360 | Reporting
	WinGetText, panel, PowerScribe 360 | Reporting
	if(!InStr(panel, ".) - ")){
			ControlSend, Main Menu, {Alt Down}{v}{o}, PowerScribe 360 | Reporting
			Sleep 50
			ControlSend, Main Menu, {Alt Up}, PowerScribe 360 | Reporting
	}
	WinGetText, panel, PowerScribe 360 | Reporting
	isSuccess := InStr(panel, ".) - ") || InStr(panel, "TEMPORARY") 
	Return, isSuccess
}

GetPowerscribeTextboxname(){
;this function gets the appropriate control for powerscribes text box
Global pscribetxtboxArr := []
Global pscribetxtbox
Global pscribetxtbox2
WinGet, CtrlList, ControlList, PowerScribe 360 | Reporting
Loop, Parse, CtrlList, `n
{
	if (InStr(A_LoopField, "RICHEDIT50W")){
		pscribetxtboxArr.Push(A_LoopField)
	}
}
	pscribetxtbox := pscribetxtboxArr[1]
	pscribetxtbox2 := pscribetxtboxArr[2]
}