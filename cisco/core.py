import win32com.client as win32
import pythoncom
from inspect import getmembers
class EventHandler:
     def OnConnectCtiSuccedEvent(strMac):
        print("OnConnectCtiSuccedEvent=" * strMac)



def com_client_verbose(client_class_name):
    title = client_class_name + " client"
    print(title)
    print("=" * len(title))
    com_client = win32.gencache.EnsureDispatch(client_class_name)
    print(type(com_client))
    print(dir(com_client))
    print("\n\n")
    return com_client

def prd_verbose(prd):
    orphan =win32.Dispatch(prd)
    orphan_events = win32.WithEvents(orphan, EventHandler)
    orphan.InitControl("192.168.1.0", "42028", "192.168.1.1", "42028", "D:\\log\\", "7001");
    #orphan.AgentLogon("81000", "81000", "123456");
    
def class_name_verbose(clsid):
    title = clsid + " module"
    print(title)
    print("=" * len(title))
    module = win32.gencache.EnsureModule(clsid, 0, 1, 2)
    print(repr(module))
    print(type(module))
    path = module.__file__
    print(path)
    #print_members(module.ICccCtrlX)
    #module.ICccCtrlX.Initial()
    # INSPECT the CODE to obtain the class name. Is this really necessary?
    # https://stackoverflow.com/questions/17225798/python-win32com-dont-know-name-of-module
    with open(path, "r") as f:
        for line in f.readlines():
            if line.startswith("# This CoClass is known by the name"):
                print(line, "\n\n")
                return line.split("'")[1]
        else:
            raise RuntimeError("CoClass comment line not found.")
    

def print_members(obj, obj_name="placeholder_name"):
    """Print members of given COM object"""
    try:
        fields = list(obj._prop_map_get_.keys())
    except AttributeError:
        print("Object has no attribute '_prop_map_get_'")
        print("Check if the initial COM object was created with"
              "'win32com.client.gencache.EnsureDispatch()'")
        raise
    methods = [m[0] for m in getmembers(obj) if (not m[0].startswith("_")
                                                 and "clsid" not in m[0].lower())]

    if len(fields) + len(methods) > 0:
        print("Members of '{}' ({}):".format(obj_name, obj))
    else:
        raise ValueError("Object has no members to print")

    print("\tFields:")
    if fields:
        for field in fields:
            print(f"\t\t{field}")
    else:
        print("\t\tObject has no fields to print")

    print("\tMethods:")
    if methods:
        for method in methods:
            print(f"\t\t{method}")
    else:
        print("\t\tObject has no methods to print")


# Most Windows machines have Excel installed. Excel exposes a COM interface.
print("\n\n")
#xl_client = com_client_verbose("Excel.Application")

# OPCEnum CLSID is documented at: http://www.opcti.com/dcom-error-for-clsid.aspx
# win32com.client.combrowse confirms that this CLSID is active on my system.
opc_enum_clsid = "{a6ef9860-c720-11d0-9337-00a0c90dcaa9}"
#opc_enum_class_name = class_name_verbose(opc_enum_clsid)

opc_enum_client = prd_verbose("ax.cti")
# Now that we have a class name for OPCEnum, try to create its COM client.
# This fails.
#opc_enum_client = com_client_verbose("ax.cti")
