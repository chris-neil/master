
vmcli "C:\Users\cneil\Documents\Virtual Machines\GaiaR82-Template\GaiaR82-Template.vmx" VMTemplate Create -p "C:\Users\cneil\Documents\Virtual Machines\vsx04\vsx04.vmtx" -n vsx04 
vmcli VMTemplate Deploy -p "C:\Users\cneil\Documents\Virtual Machines\vsx04\vsx04.vmtx"

vmcli "C:\Users\cneil\Documents\Virtual Machines\vsx04\vsx04.vmx" Chipset SetVCpuCount 2
vmcli "C:\Users\cneil\Documents\Virtual Machines\vsx04\vsx04.vmx" Chipset SetMemSize 4096
vmcli "C:\Users\cneil\Documents\Virtual Machines\vsx04\vsx04.vmx" Chipset SetCoresPerSocket 2

vmcli "C:\Users\cneil\Documents\Virtual Machines\vsx04\vsx04.vmx" Snapshot Take "AfterClone"

vmcli "C:\Users\cneil\Documents\Virtual Machines\vsx04\vsx04.vmx" Power Start
