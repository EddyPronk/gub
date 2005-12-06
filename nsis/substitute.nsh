;;;; lilypond.nsi -- LilyPond installer script for Microsoft Windows
;;;; (c) 2005 Jan Nieuwenhuizen <janneke@gnu.org>
;;;; licence: GNU GPL

;; inspired on
;; http://nsis.sourceforge.net/archive/nsisweb.php?page=560&instances=0,311

!include "StrFunc.nsh"
${StrRep}

Function CopyFileWithCallback
	Exch $R0 ;input file name
	Exch
	Exch $R1 ;output file name
	Exch
	Exch $R2 ;callback
	Push $R3 ;input handle
	Push $R4 ;output handle
	Push $R5 ;string

	ClearErrors
  	FileOpen $R3 $R0 r
	IfErrors exit
  	FileOpen $R4 $R1 w
	IfErrors cleanup loop
cleanup:
	FileClose $4
	SetDetailsPrint none
  	Delete $R1
   	SetDetailsPrint both
	Goto exit
loop:
 	ClearErrors
 	FileRead $R3 $R5
 	Push $R5
 	Call $R2
 	Pop $R5
 	IfErrors closeup
 	FileWrite $R4 $R5
	Goto loop
closeup:
  	FileClose $R4
exit:
  	FileClose $R3
	Pop $R5
	Pop $R4
	Pop $R3
	Pop $R2
	Pop $R1
	Pop $R0
FunctionEnd

Function SubstituteAtVariablesCallback
	Push $R0
	Exch

	Push "@DESKTOP@"
	Push "$UP_DESKTOP"
	Call StrRep

	Push "@EDITOR@"
	Push "$EDITOR"
	Call StrRep

	Push "@INSTDIR@"
	Push "$INSTDIR"
	Call StrRep

	Push "@BUNDLE_VERSION@"
	Push "${BUNDLE_VERSION}"
	Call StrRep

	Push "@GUILE_VERSION@"
	Push "${GUILE_VERSION}"
	Call StrRep

	Push "@LILYPOND_VERSION@"
	Push "${LILYPOND_VERSION}"
	Call StrRep

	Push "@PYTHON_VERSION@"
	Push "${PYTHON_VERSION}"
	Call StrRep

	Push "@SLASHED_INSTDIR@"
	Push "$INSTDIR"
	Push "\"
	Push "/"
	Call StrRep
	Call StrRep

	Push "@WINDIR@"
	Push "$WINDIR"
	Call StrRep

	Exch
	Pop $R0
FunctionEnd

!macro SubstituteAtVariables InFile OutFile
	Push $R0

	GetFunctionAddress $R0 SubstituteAtVariablesCallback
	Push $R0
	Push "${OutFile}"
	Push "${InFile}"
	Call CopyFileWithCallback

	Pop $R0
!macroend
!define SubstituteAtVariables "!insertmacro SubstituteAtVariables"


Function SubstituteBackslashesCallback
	Push $R0
	Exch

	Push "\\"
	Push "/"
	Call StrRep

	Push "\"
	Push "/"
	Call StrRep

	Exch 
	Pop $R0
FunctionEnd

!macro SubstituteBackslashes InFile OutFile
	Push $R0

	GetFunctionAddress $R0 SubstituteBackslashesCallback
	Push $R0
	Push "${OutFile}"
	Push "${InFile}"
	Call CopyFileWithCallback

	Pop $R0
!macroend
!define SubstituteBackslashes "!insertmacro SubstituteBackslashes"
