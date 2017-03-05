

# example filepath to uri resolve:
# 
# from uri_resolver import resolver
# f = "/mnt/ala/jobs/s171/assets/Prop/Machine_Debri002/model/publish/caches/MachineDebri002.v005.abc"
# print resolver.filepath_to_uri(f, "filesystem")
#
# result:
# /mnt/ala/jobs/s171/assets/Prop/Machine_Debri002/model/publish/caches/MachineDebri002.$VERSION.abc


# example uri to filepath resolve
#
# from uri_resolver import resolver
# f = "/mnt/ala/jobs/s171/assets/Prop/Machine_Debri002/model/publish/caches/MachineDebri002.005.abc"
# print resolver.filepath_to_uri(f, "filesystem")
#
# result:
# /mnt/ala/jobs/s171/assets/Prop/Machine_Debri002/model/publish/caches/MachineDebri002.005.ab
