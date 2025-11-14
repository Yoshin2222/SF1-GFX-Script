
if __name__ == "__main__":
#Init
    import os

    def verify_folder(path):
        if not os.path.exists(path):
            os.makedirs(path)
    
    def verify_ROMs(rom_path,game_name,GFX):
        bool = ["Does not Exist",
                "Exists"]
        ret = 1
        for key in GFX:
            print("\tVerifying {}...".format(key))
            for index in GFX[key]["ROMS"]:
                rom = GFX[key]["ROMS"][index][0]
                path = os.path.join(rom_path,game_name,rom)
                check = os.path.exists(path)
                print("\t\t{} - {}".format(path,bool[check]))
                if check == 0:
                    ret = 0
        return ret
    
    def verify_interleaved_files(GFX):
        bool = ["Does not Exist",
                "Exists"]
        ret = 1

        for key in GFX:
            outpath = os.path.join(paths["Out_Path"],"{} - {}".format(key, GFX[key]["TYPE"]))#
            check = os.path.exists(outpath)
            if check == 0:
                ret = 0
            print("{} - {}".format(outpath,bool[check]))
#            print(outpath)
        return ret

    def de_interleave_GFX(GFX,game_name):
        print("\nDe-interleaving GFX...")
        cases = {
            "CHAR" : de_interleave_char,
            "SPRITES" : de_interleave_sprites,
        }
        check = verify_interleaved_files(GFX)
        if check == 0:
            print("Some Interleaved files don't exist!")
        else:
            for key in GFX:
                outpath = os.path.join(paths["Out_Path"],"{} - {}".format(key, GFX[key]["TYPE"]))#
                print("De-interleaving {}...".format(outpath))
                with open(outpath,"rb") as inp:
                    temp_dat = inp.read()
                temp_dat = cases[GFX[key]["TYPE"]](temp_dat)
                output_ROMs(temp_dat,GFX[key],game_name)
 
    def output_ROMs(*arg):
        index = 0
        for key in arg[1]["ROMS"]:
            out_name = os.path.join(paths["ROM_Path"],arg[2],arg[1]["ROMS"][key][0])
            temp = arg[0][index:index + arg[1]["ROMS"][key][1]]
            index += arg[1]["ROMS"][key][1]
            print("Outputting {}...".format(out_name))
            with open(out_name,"wb") as out:
                out.write(bytes(temp))

    def de_interleave_char(*arg):
        dat = []
        for x in range(0,len(arg[0]),2):
            dat.append((arg[0][x] & 0xf0) + ((arg[0][x+1] & 0xf0) >> 4))
            dat.append(((arg[0][x] & 0x0f) << 4) + (arg[0][x+1] & 0x0f))
        return dat

    def de_interleave_sprites(*arg):
        dat = [0] * len(arg[0])
        print(hex(len(arg[0])))
        half_size = (len(arg[0])>>1)
        for i in range(0,len(arg[0])>>1,2):
            inp = i<<1
            adr1,adr2 = i,i + half_size
            dat[adr2] = (arg[0][inp]&0xf0) + ((arg[0][inp+1]&0xf0)>>4)
            dat[adr2+1] = ((arg[0][inp]&0x0f)<<4) + ((arg[0][inp+1]&0x0f))
            dat[adr1] = (arg[0][inp+2]&0xf0) + ((arg[0][inp+3]&0xf0)>>4)
            dat[adr1+1] = ((arg[0][inp+2]&0x0f)<<4) + ((arg[0][inp+3]&0x0f))
        print(hex(len(dat)))
        return dat

    def interleave_GFX(paths,game_name,GFX):
        cases = {
            "CHAR" : interleave_char,
            "SPRITES" : interleave_sprites,
        }

        print("\nInterleaving GFX...")
        check = verify_ROMs(paths["ROM_Path"],game_name,GFX)
        if check == 0:
            print("Some ROMs don't exist!")
        else:
        #Make temporary copies, verify the ROMs exist while we're here
            for key in GFX:
#                temp_files = {}
                temp_dat = []
                out_dat = []
                for index in GFX[key]["ROMS"]:
                    group = GFX[key]["ROMS"]
                    rom = group[index][0]
                    path = os.path.join(paths["ROM_Path"],game_name,rom)
                    with open(path,"rb") as inp:
                        temp_dat += inp.read()
                print("Interleaving {} - TYPE = [ {} ] - {}...".format(key,GFX[key]["TYPE"],hex(len(temp_dat))))
                out_dat = cases[GFX[key]["TYPE"]](temp_dat)

                #Write to a file
                outpath = os.path.join(paths["Out_Path"],"{} - {}".format(key, GFX[key]["TYPE"]))
                with open(outpath,"wb") as out:
                    out.write(bytes(out_dat))
                print("Writing {}".format(outpath))

    #It seems that data is split into 4 pixels, 2 of which being grabbed from the first half of the data,
    #the next from the latter, so if the total data is 0x80000 in length, the first 2 pixels would be from
    #0x00/0x01, and the next 2 would be from 0x40000/0x40001

    def interleave_sprites(*arg):
        dat = []
        half_size = (len(arg[0])>>1)
        for i in range(0,len(arg[0])>>1,2):
            adr1,adr2 = i,i + half_size
            dat.append((arg[0][adr2] & 0xf0) + ((arg[0][adr2+1] & 0xf0) >> 4))
            dat.append(((arg[0][adr2] & 0x0f) << 4) + (arg[0][adr2+1] & 0x0f))
            dat.append((arg[0][adr1] & 0xf0) + ((arg[0][adr1+1] & 0xf0) >> 4))
            dat.append(((arg[0][adr1] & 0x0f) << 4) + (arg[0][adr1+1] & 0x0f))
        return dat
    
    #The idea is each line of a tile is composed of of 8 bits between 2 bytes, the first line being the upper 4 bits
    #of each, the next the lower. Simple enough to shuffle the bits around
    #Ya can think of it as converting this
    #xxxxyyyy xxxxyyyy
    #to this
    #xxxxxxxx yyyyyyyy
    def interleave_char(*arg):
        dat = []
        for x in range(0,len(arg[0]),2):
            dat.append((arg[0][x] & 0xf0) + ((arg[0][x+1] & 0xf0) >> 4))
            dat.append(((arg[0][x] & 0x0f) << 4) + (arg[0][x+1] & 0x0f))
        return dat

    def select_action(paths,game_name,GFX):
        action = input("Please select what you would like to do\n 1 - Interleave \t0 - De-Interleave\n")
        match action:
            case "1":
                interleave_GFX(paths,game_name,GFX)
                print("Finished!\n")
            case "2":
                de_interleave_GFX(GFX,game_name)
                print("Finished!\n")
            case _:
                print("\nInvalid Command!\n")


    #SF1 has 2 kinds of GFX, 16x16 sprite/BG tiles which are 4bpp, and 8x8 Char tiles which are 2bpp for stuff like Text
    GFX = {
        "GFX1" : {
                "TYPE" : "SPRITES",
                "ROMS" : {
                    0 : ["sf-39.2k", 0x020000],
                    1 : ["sf-38.1k", 0x020000],
                    2 : ["sf-41.4k", 0x020000],
                    3 : ["sf-40.3k", 0x020000],
                },
            },
        "GFX2" : {
                "TYPE" : "SPRITES",
                "ROMS" : {
                    0 : ["sf-25.1d", 0x020000],
                    1 : ["sf-28.1e", 0x020000],
                    2 : ["sf-30.1g", 0x020000],
                    3 : ["sf-34.1h", 0x020000],
                    4 : ["sf-26.2d", 0x020000],
                    5 : ["sf-29.2e", 0x020000],
                    6 : ["sf-31.2g", 0x020000],
                    7 : ["sf-35.2h", 0x020000],
                },
            },
        "GFX3" : {
                "TYPE" : "SPRITES",
                "ROMS" : {
                    0 : ["sf-15.1m", 0x020000],
                    1 : ["sf-16.2m", 0x020000],
                    2 : ["sf-11.1k", 0x020000],
                    3 : ["sf-12.2k", 0x020000],
                    4 : ["sf-07.1h", 0x020000],
                    5 : ["sf-08.2h", 0x020000],
                    6 : ["sf-03.1f", 0x020000],
                    7 : ["sf-17.3m", 0x020000],
                    8 : ["sf-18.4m", 0x020000],
                    9 : ["sf-13.3k", 0x020000],
                    10 : ["sf-14.4k", 0x020000],
                    11 : ["sf-09.3h", 0x020000],
                    12 : ["sf-10.4h", 0x020000],
                    13 : ["sf-05.3f", 0x020000],
                },
            },
            "GFX4" : {
                "TYPE" : "CHAR",
                "ROMS" : {
                    0 : ["sf-27.4d",0x004000],
                },
            },
}
    paths = {"ROM_Path" : r"ROMs",
            "Out_Path" : r"Out",
             }
    for key in paths:
        verify_folder(paths[key])        

    print("----\tYoshins SF1 GFX Tool\t----")
    while 1:
        select_action(paths,"sf",GFX)