;;;; lilypond.nsi -- LilyPond installer script for Microsoft Windows
;;;; (c) 2005--2007
;;;; Jan Nieuwenhuizen <janneke@gnu.org>
;;;; Han-Wen Nienhuys <janneke@gnu.org>
;;;; licence: GNU GPL

;; For quick [wine] test runs
;; !define TEST "1"


;;; substitutions

!define ENVIRON "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"

!define UNINSTALL \
	"Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRETTY_NAME}"
!define USER_SHELL_FOLDERS \
	"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"


Var "EDITOR"
Var "UP_DESKTOP"

!define UninstLog "files.txt"
Var UninstLog

; Uninstall log file missing.
LangString UninstLogMissing ${LANG_ENGLISH} "${UninstLog} not found.$\r$\nCannot uninstall."

!include "substitute.nsh"
${StrLoc}
${UnStrLoc}

;;SetCompressor lzma  ; very slow
;;SetCompressor zlib
SetCompressor bzip2  ;;

Name "${PRETTY_NAME}"

Caption "${PRETTY_NAME} ${INSTALLER_VERSION} for Microsoft Windows"
BrandingText "${PRETTY_NAME} installer v1.0"


InstallDir $PROGRAMFILES\${PRETTY_NAME}
InstallDirRegKey HKLM "Software\${PRETTY_NAME}" "Install_Dir"

CRCCheck on
XPStyle on
InstallColors /windows

BGGradient 000000 E8FFE8 FFFFFF

;; Use Finish iso Close for the [close button text]
;; Although nothing happens after Close, experienced Windows users feel
;; much more with "Finish" than with Close.
MiscButtonText Back Next Cancel Finish

LicenseText "Conditions for redistributing ${PRETTY_NAME}" "Next"
LicenseData "${ROOT}\license\${NAME}"
LicenseForceSelection off

Page license

;; FIXME: the intstaller will crash on File /r commands if Page
;; directory is not used.
Page directory

Page components
Page instfiles

UninstPage uninstConfirm
UninstPage instfiles

Section "${PRETTY_NAME} (required)"
	;; In silent mode (invoke as: setup.exe /S), generate an install log.
	ifSilent 0 silent
	Logset on
silent:

	IfFileExists $INSTDIR\usr\bin\${CANARY_EXE}.exe no_overwrite_error fresh_install
no_overwrite_error:
	MessageBox MB_OK "Previous version of ${PRETTY_NAME} found$\r$\nUninstall the old version first."
	Abort "Previous version of ${PRETTY_NAME} found$\r$\nUninstall the old version first."

fresh_install:


	SetOverwrite on
	AllowSkipFiles on
	SetOutPath $INSTDIR

        File /r "${ROOT}\usr"
        File /r "${ROOT}\license"
        File /r "${ROOT}\files.txt"

	WriteUninstaller "uninstall.exe"
	CreateDirectory "$INSTDIR\usr\bin"

	Call registry_installer

	;; Use tested lilypad for now
	StrCpy $EDITOR "$INSTDIR\usr\bin\lilypad.exe"

	;; FIXME: what is UP_DESKTOP used for?
	Call find_desktop

	Call registry_guile
	Call registry_lilypond

	;; FIXME: these postinstall things should be part of their
	;; respective packages once we have min-apt or Cygwin's
	;; setup.exe in place.

	Call postinstall_lilypond
	Call postinstall_lilypad


SectionEnd

;; Optional section (can be disabled by the user)
Section "Bundled Python"
    ;; Only make bundled python interpreter the default
    ;; if user wants it to be (i.e.  for the average windows
    ;; user who only cares that software works just like that)
    Call registry_python
SectionEnd


;; Optional section (can be disabled by the user)
Section "Start Menu Shortcuts"
	;; First install for all users, if anything fails, install
	;; for current user only.
	ClearErrors

	;; The OutPath specifies the CWD of the command.  For desktop
	;; shortcuts, set to a string that expands to the desktop folder
	;; of the user who runs LilyPond.
	ReadRegStr $R0 HKCU "${USER_SHELL_FOLDERS}" "Desktop"
	SetOutPath '"$R0"'
	SetShellVarContext all

        ;; Working directory: %USERPROFILE%\<locale's-desktop-folder-name>,
	;; but that string is not expanded.

	;; Let's see what happens when outputting to the shared desktop.
	SetOutPath "$DESKTOP"
	Call create_shortcuts

	;; That also did not work, often the other users do no write access
	;; there.

	;; If no write access for all, delete common stuff and opt for
	;; install for current user only.
	IfErrors 0 exit
	Delete "$DESKTOP\LilyPond.lnk"
	Delete "$SMPROGRAMS\LilyPond\*.*"
	RMDir "$SMPROGRAMS\LilyPond"

	;; $DESKTOP should expand to the same location as the outpath above,
	;; but nsis may handle anomalies better.
current_user:
	SetShellVarContext current
	SetOutPath "$DESKTOP"
	Call create_shortcuts
exit:
	SetShellVarContext current
	SetOutPath $INSTDIR
SectionEnd


;; copy & paste from the NSIS code examples 
Function un.install_installed_files
 IfFileExists "$INSTDIR\${UninstLog}" +3
  MessageBox MB_OK|MB_ICONSTOP "$(UninstLogMissing)"
   Abort
 
 Push $R0
 Push $R1
 Push $R2
 SetFileAttributes "$INSTDIR\${UninstLog}" NORMAL
 FileOpen $UninstLog "$INSTDIR\${UninstLog}" r
 StrCpy $R1 0
 
 GetLineCount:
  ClearErrors
   FileRead $UninstLog $R0
   IntOp $R1 $R1 + 1
   IfErrors 0 GetLineCount
 
 LoopRead:
  FileSeek $UninstLog 0 SET
  StrCpy $R2 0
  FindLine:
   FileRead $UninstLog $R0
   IntOp $R2 $R2 + 1
   StrCmp $R1 $R2 0 FindLine
 
   StrCpy $R0 "$INSTDIR\$R0" -2
   IfFileExists "$R0\*.*" 0 +3
    RMDir $R0  #is dir
   Goto +3
   IfFileExists "$R0" 0 +2
    Delete "$R0" #is file
 
  IntOp $R1 $R1 - 1
  StrCmp $R1 0 LoopDone
  Goto LoopRead
 LoopDone:
 FileClose $UninstLog

 Pop $R2
 Pop $R1
 Pop $R0

FunctionEnd
;; end copy & paste


Section "Uninstall"
	ifSilent 0 silent
	Logset on
silent:
	DeleteRegKey HKLM SOFTWARE\${PRETTY_NAME}
	DeleteRegKey HKLM "Applications\lilypond-windows.exe"
	DeleteRegKey HKLM "${UNINSTALL}"

	DeleteRegKey HKCR ".ly"
	DeleteRegKey HKCR "ly_auto_file"
	DeleteRegKey HKCR "${PRETTY_NAME}\shell\open\command" ""
	DeleteRegKey HKCR "${PRETTY_NAME}\shell\generate\command" ""
	DeleteRegKey HKCR "${PRETTY_NAME}\DefaultIcon" ""
	DeleteRegKey HKCR "${PRETTY_NAME}" ""

	DeleteRegKey HKCR "textedit" ""

	DeleteRegKey HKCR ".scm"
	DeleteRegKey HKCR "GUILE\shell\open\command" ""
	DeleteRegKey HKCR "GUILE" ""

	DeleteRegKey HKCU "Applications\lilypond-windows.exe"
	DeleteRegKey HKCU ".ly"


    	ReadRegStr $R0 HKLM "${ENVIRON}" "PATH"
 	${UnStrLoc} $0 $R0 "$INSTDIR\usr\bin;" >
path_loop:
	StrCmp $0 "" path_done
	StrLen $1 "$INSTDIR\usr\bin;"
	IntOp $2 $0 + $1
	StrCpy $3 $R0 $0 0
	StrCpy $4 $R0 10000 $2
	WriteRegExpandStr HKLM "${ENVIRON}" "PATH" "$3$4"
	ReadRegStr $R0 HKLM "${ENVIRON}" "PATH"
	${UnStrLoc} $0 $R0 "$INSTDIR\usr\bin;" >
	StrCmp $0 "" path_done path_loop

path_done:
	;; Remove files and uninstaller
	;; Try only to delete ${PRETTY_NAME} (and not user) stuff

	Delete "$INSTDIR\usr\bin\variables.sh.in"
	Delete "$INSTDIR\usr\bin\variables.sh"
	Delete "$INSTDIR\usr\bin\lilypond-windows.bat.in"

	call un.install_installed_files

	;; Remove shortcuts, if any
        SetShellVarContext all
	Delete "$SMPROGRAMS\${PRETTY_NAME}\*.*"
	Delete "$DESKTOP\${PRETTY_NAME}.lnk"
	RMDir "$SMPROGRAMS\${PRETTY_NAME}"

	SetShellVarContext current
	Delete "$SMPROGRAMS\${PRETTY_NAME}\*.*"
	Delete "$DESKTOP\${PRETTY_NAME}.lnk"
	RMDir "$SMPROGRAMS\${PRETTY_NAME}"

	;; Remove directories used
	RMDir "$SMPROGRAMS\${PRETTY_NAME}"
	RMDir "$INSTDIR\usr\bin"
	RMDir "$INSTDIR\usr\"
	Delete "$INSTDIR\uninstall.exe"
	Delete "$INSTDIR\files.txt"
	RMDir "$INSTDIR"
SectionEnd

Function registry_installer
	WriteRegStr HKLM "SOFTWARE\${PRETTY_NAME}" "Install_Dir" "$INSTDIR"
	WriteRegStr HKLM "${UNINSTALL}" "DisplayName" "${PRETTY_NAME}"
	WriteRegStr HKLM "${UNINSTALL}" "UninstallString" '"$INSTDIR\uninstall.exe"'
	WriteRegDWORD HKLM "${UNINSTALL}" "NoModify" 1
	WriteRegDWORD HKLM "${UNINSTALL}" "NoRepair" 1
FunctionEnd

!include "lilypond-prepost.nsh"


Function find_desktop
	ReadRegStr $R0 HKCU "${USER_SHELL_FOLDERS}" "Desktop"
	StrCpy $UP_DESKTOP "$R0"
	StrCmp $UP_DESKTOP "" 0 exit
	StrCpy $UP_DESKTOP "%USERPROFILE%\Desktop"
exit:
FunctionEnd

