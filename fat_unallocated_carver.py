#-*- coding: utf-8 -*-

import sys
import struct

def VBR(vbr):
	print("==============FAT VBR==============")
	print()

	global bytes_per_sector, reserved_sector_count
	global size_of_fat, reserved_size, cluster_size, fat_size, data_area_start, total_volume_size

	bytes_per_sector = struct.unpack_from("<H", vbr, 0xb)[0]
	print("Bytes per Sector:", bytes_per_sector)

	sectors_per_cluster = struct.unpack_from(">B",vbr, 0xd)[0]
	print("Sectors per Cluster:", sectors_per_cluster)

	reserved_sector_count = struct.unpack_from("<H",vbr,0xe)[0]
	print("Reserved Sector Count:", reserved_sector_count)

	number_of_fat = struct.unpack_from("<H", vbr, 0x10)[0]
	print("Number of Fats:", number_of_fat)

	total_sector = struct.unpack_from("<I", vbr, 0x20)[0]
	print("Total Sector:", total_sector)

	size_of_fat = struct.unpack_from("<I",vbr, 0x24)[0]
	print("Size of FAT:", size_of_fat)

	volume_label = struct.unpack_from("<10s",vbr,0x47)[0]
	print("Volume Label:", volume_label.decode('UTF-8'))

	filesystem_type = struct.unpack_from("<8s",vbr,0x52)[0]
	print("FileSystem Type:", filesystem_type.decode('UTF-8'))

	reserved_size = reserved_sector_count*bytes_per_sector
	print("Reserved Size:", hex(reserved_size))

	fat_size = int(bytes_per_sector*size_of_fat)
	print("Fat Size:", hex(fat_size))

	cluster_size = sectors_per_cluster * bytes_per_sector
	print("Cluster Size:", cluster_size)

	data_area_start = reserved_size + fat_size*number_of_fat
	print("Data Area Start:", hex(data_area_start))

	total_volume_size = total_sector*bytes_per_sector
	print("Total Volume Size:", hex(total_volume_size))
   	
def Fsinfo(vol_h):
	print("==============FAT Fsinfo==============")
	print()
	#FsInfo Lead Signature
	fsinfo_lead_signature = struct.unpack_from("<I", vol_h, 0x0)[0]
	print("Fsinfo Lead Signature : ", hex(fsinfo_lead_signature))

	#FsInfo Sruct Signature
	fsinfo_struct_signature = struct.unpack_from("<I", vol_h, 0x1E4)[0]
	print("Fsinfo Sturct Signature : ", hex(fsinfo_struct_signature))

	#FsInfo tail Signature
	fsinfo_footer_signature = struct.unpack_from("<H", vol_h, 0x1FE)[0]
	print("Fsinfo Footer Signature : ", hex(fsinfo_footer_signature))

def Fat_1(fat_start):
	print("==============FAT==============")
	print()

	for i in range(2, fat_size//4+1-4):
		address = 0x4*i
		data_cluster = struct.unpack_from("<I", fat_start, address)[0]
		if data_cluster == 0:
			data_area_location = data_area_start + cluster_size*(i-2)
			
			f.seek(data_area_location)
			data = f.read(cluster_size)

			file_signature = struct.unpack_from(">I", data, 0x0)[0]

			if(Extract_file(file_signature, data) == 1):
				print(str(i-1)+"-png")
			elif(Extract_file(file_signature, data) == 2):
				print(str(i-1)+"-jpeg")
			elif(Extract_file(file_signature, data) == 3):
				print(str(i-1)+"-pdf")
			elif(Extract_file(file_signature, data) == 4):
				print(str(i-1)+"-zip[docx]")
			elif(Extract_file(file_signature, data) == 5):
				print(str(i-1)+"-zip[xlsx]")
			elif(Extract_file(file_signature, data) == 6):
				print(str(i-1)+"-zip[pptx]")
			elif(Extract_file(file_signature, data) == 7):
				zip_file_name_length = struct.unpack_from("<H", data, 0x1a)[0]
				zip_file_name = struct.unpack_from("<"+str(zip_file_name_length)+"s", data, 0x1e)[0]
				print(str(i-1)+"-zip"+"{"+str(zip_file_name.decode('UTF-8'))+"}")
			else:
				continue
			
		else:
			continue
	
def Extract_file(file_signature, data):
	#png
	if file_signature == 0x89504e47:
		return 1
	#jpeg
	elif (file_signature == 0xffd8ffe0) or (file_signature == 0xffd8ffe1) or (file_signature == 0xffd8ffe8):
		return 2
	#pdf
	elif file_signature == 0x25504446:
		return 3
	#docx, xlsx, pptx
	elif file_signature == 0x504b0304:
		docu_signature = 0x14000600
		file_signature_plus = struct.unpack_from(">I", data, 0x4)[0]
		if(hex(file_signature_plus) == hex(docu_signature)):
			if data.hex().find("776f7264") != -1:
				return 4
			elif data.hex().find("786c") != -1:
				return 5
			elif data.hex().find("707074") != -1:
				return 6
		else:
			return 7

def select_menu():
	print("************************************************")
	print("************************************************\n")
	print("Welcome to FAT carver!!")
	print("\n************************************************")
	print("************************************************\n")
	volume_name = input("Put want to see volume: ")
	return volume_name

def main(volume_name):
	# volume open
	global f
	try:
		f = open("\\\\.\\"+volume_name+":", "rb")
	
		# Get vbr
		f.seek(0)
		vbr = f.read(512)
		VBR(vbr)

		# Get fsinfo
		f.seek(512)
		vol_h = f.read(512)
		Fsinfo(vol_h)

		# Get fat
		fat_start = bytes_per_sector*reserved_sector_count
		f.seek(fat_start)
		fat_start = f.read(fat_size)
		Fat_1(fat_start)
	except:
		print("Push right volume name")

if __name__ == "__main__":
	volume_name = select_menu()
	main(volume_name)