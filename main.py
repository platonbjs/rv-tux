import atexit
import config as cfg
from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim


def print_vm_info(vm, depth=1, max_depth=10):
    """
    Print information for a particular virtual machine or recurse into a
    folder with depth protection
    """

    # if this is a group it will have children. if it does, recurse into them
    # and then return
    if hasattr(vm, 'childEntity'):
        if depth > max_depth:
            return
        vmList = vm.childEntity
        for c in vmList:
            print_vm_info(c, depth + 1)
        return
    videoCard = get_videoCard(vm)
    summary = vm.summary
    vm_info = {
        "VM": summary.config.name,
        "Powerstate": summary.runtime.powerState,
        "Template": summary.config.template,
        "Config status": vm.configStatus,
        "DNS Name": summary.guest.hostName,
        "connection state": summary.runtime.connectionState,
        "Guest state": summary.guest.toolsRunningStatus,
        "Heartbeat": summary.quickStats.guestHeartbeatStatus,
        "Consolidation Needed": summary.runtime.consolidationNeeded,
        "PowerOn": summary.runtime.bootTime,
        "Suspend time": summary.runtime.suspendTime,
        "Change Version": vm.config.changeVersion,
        "CPUs": summary.config.numCpu,
        "Latency Sensivity": None if vm.config.latencySensitivity is None else vm.config.latencySensitivity.level,
        "Memory": summary.config.memorySizeMB,
        "NICs": summary.config.numEthernetCards,
        "Disks": summary.config.numVirtualDisks,
        "EnableUUID": vm.config.flags.diskUuidEnabled,
        "CBT": vm.config.changeTrackingEnabled,
        "Network #1": vm.network[0].name if summary.config.numEthernetCards >0 else None,
        "Network #2": vm.network[1].name if summary.config.numEthernetCards >1 else None,
        "Network #3": vm.network[2].name if summary.config.numEthernetCards >2 else None,
        "Network #4": vm.network[3].name if summary.config.numEthernetCards >3 else None,
        "Num Monitors": videoCard.numDisplays,
        "Video Ram KB": videoCard.videoRamSizeInKB,
        "Resource pool": vm.resourcePool.config.name
    }
    print(vm_info)

def get_videoCard(vm):
    for device in vm.config.hardware.device:
        if (type(device).__name__ == "vim.vm.device.VirtualVideoCard"):
            return device
    return None

try:
    service_instance = connect.SmartConnectNoSSL(host=cfg.credentials["host"],
                                                user=cfg.credentials["user"],
                                                pwd=cfg.credentials["password"],)
    content = service_instance.RetrieveContent()
    object_view = content.viewManager.CreateContainerView(content.rootFolder,[], True)
    for obj in object_view.view:
        if isinstance(obj, vim.VirtualMachine):
            print_vm_info(obj)
    object_view.Destroy()
    atexit.register(connect.Disconnect, service_instance)
except vmodl.MethodFault as e:
    print("Caught vmodl fault : " + e.msg)