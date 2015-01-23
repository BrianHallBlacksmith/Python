import arcgisscripting,sys,os,math,string
#ע�⣺���ﲻҪ����gp=arcgisscripting.create(9.3)����������һЩ���(��gp.getrasterproperties())��ȡ��ֵ��object��������ֵ��
gp=arcgisscripting.create()

#���սű����ߴ����Ĳ���
ws=gp.getparameterastext(0)
dem_input=gp.getparameterastext(1)#����DEM�̸߳�����������
wshed=gp.getparameterastext(2)#��������߽�������ݣ����ü�LS����֮��
demunits=gp.getparameterastext(3)#����DEM��λ��meters��feet,Ĭ��Ϊmeters
scf_lt5=gp.getparameterastext(4)#scf_lt5=0.7
scf_ge5=gp.getparameterastext(5)#scf_ge5=0.5
gp.workspace=ws
#���巵�ش�����
def sendmsg(msg):
    print msg
    gp.addmessage(msg)
gp.overwriteoutput=1
#�ж�ָ����Ŀ¼�Ƿ����
if not gp.Exists(ws):
    sendmsg( "ָ��Ŀ¼������")
else:
    sendmsg( "ָ��Ŀ¼���ڣ����Լ���������")

#�ж�����DEM���ݵ�ˮƽ�ʹ�ֱ����ĵ�λ�Ƿ�һ��
if demunits==None or demunits.strip()=="":
    demunits="meters"
    sendmsg("ʹ��Ĭ�ϵ�λ��meters")
elif demunits!="meters" and demunits!="feet":
    demunits="meters"
    sendmsg( "DEM��λ��������,ʹ��Ĭ�ϵ�λmeters")
#���ý���/��ʼ�³��ۼƵ��ж����ӣ�ΪС�ڻ���ڵ���5�ȵ������ò�ͬ�Ĳ���
#�����¶�С��5��ʱ������ֵΪ0.7�����ڵ���5��ʱ������ֵΪ0.5

#scf_lt5,scf_ge5ֵ����С��1.1��������Ĭ��ֵ��
if scf_lt5>=1.1:
    scf_lt5=0.7
    if scf_ge5>=1.1:
        scf_ge5=0.5
else:
    if scf_ge5>=1.1:
        scf_ge5=0.5
sendmsg(str(scf_lt5)+","+str(scf_ge5))

#ͨ��Describe������ȡ����DEM���ݵķ�Χ�ͷֱ��ʴ�С
dem_des=gp.describe(dem_input)
cell_W=dem_des.MeanCellWidth
cell_H=dem_des.MeanCellHeight
cell_size=max(cell_W,cell_H)#��������߿�һ����ȡ���ֵ
#����һ�������������ַ������ꡢcellsize������������ƽ�ƺ���ַ�������ֵ��Ŀ��Ϊ����ԭʼС��λ������
def StoS(s,cellsize,mult):
    stri=s.split('.')
    inte=float(stri[0])+mult*cellsize
    return str(int(inte))+'.'+stri[1]
extent=dem_des.Extent.split(" ")
extent_nor=dem_des.Extent
extent_buf=StoS(extent[0],cell_size,-1)+" "+StoS(extent[1],cell_size,-1)+" "+StoS(extent[2],cell_size,1)+" "+StoS(extent[3],cell_size,1)
sendmsg("ԭʼDEM��ΧΪ��"+dem_des.Extent)
sendmsg("��һ�����������ķ�Χ��"+extent_buf)

sendmsg("�������DEM����dem_fill")
#���Spatial����Ȩ�ޣ�����Ҫ��һ��
gp.CheckOutExtension("Spatial")

#gp.Fill_sa(dem_input,"dem_fill")
#ʹ��Hickey��ArcGIS�Դ�Fill���ܵ��޸Ĺ������DEM;���㷨ʹ��һ��������Բ�����ڵ����ݵظ������ð������������СֵӦ�����ݵظ���
gp.Extent="MAXOF"
gp.Extent=extent_nor
gp.CellSize=cell_size
if gp.Exists("dem_fill"):
    gp.delete_management("dem_fill")
if gp.Exists("dem_fill2"):
    gp.Delete_management("dem_fill2")
gp.MultiOutputMapAlgebra_sa("dem_fill = "+dem_input)
finished=0
while not finished==1:
    finished=1
    gp.rename_management("dem_fill","dem_fill2")
    gp.MultiOutputMapAlgebra_sa("dem_fill = con(focalflow(dem_fill2) == 255 , focalmin(dem_fill2 , annulus ,1,1) , dem_fill2 )")
    gp.MultiOutputMapAlgebra_sa("test_grid = con(focalflow(dem_fill2) == 255 , 0 , 1 )")
    gp.Delete_management("dem_fill2")
    try:
        finished=gp.GetRasterProperties("test_grid","MINIMUM")
    except:
        sendmsg(gp.GetMessages(2))
    gp.Delete_management("test_grid")
sendmsg("���ݰ��������ֵ����ÿ���������������������")
if gp.Exists("flowdir_in"):
    gp.Delete_management("flowdir_in")
gp.FocalFlow_sa("dem_fill","flowdir_in")
if gp.Exists("flowdir_out"):
    gp.Delete_management("flowdir_out")
gp.FlowDirection_sa("dem_fill","flowdir_out")

#��������Environment��ExtentΪ����һ��������С�ķ�Χ
gp.Extent="MAXOF"
gp.Extent=extent_buf
sendmsg("Ϊdem_fill����һ��������С�Ļ���")
if gp.Exists("dem_fill_b"):
    gp.Delete_management("dem_fill_b")
gp.MultiOutputMapAlgebra_sa("dem_fill_b = con(isnull(dem_fill),focalmin(dem_fill),dem_fill)")
gp.Delete_management("dem_fill")
#����ֱ�ǵĺͶԽ��ߵ��������ʱ�ĸ�������
cellorth=1.00*cell_size
celldiag=cell_size*(2**0.5)
#Ϊÿ�����������½���downslope���ǣ���������ǰ���벢��������ƽ�ظ�����Ĭ��0.0�ȣ���û����������>0.00��<0.57(inv. tan of 1% gradient)������ֵ0.1���µļ��������и�����ʹʵ������ƽ�ı���ɺ�������>0.00���¶ȣ��Ᵽ֤�����и����������������йأ�������Ա����¶ȽǺ����յ�LS����ֵ��Ȼ������Ҫ�ǳ�С��
sendmsg("Ϊÿ�����������½���downslope����")
deg=180.0/math.pi
if gp.Exists("down_slp_ang"):
    gp.Delete_management("down_slp_ang")
dem_fill_des=gp.describe("dem_fill_b")#��������ʹ��SHIFT����ʱ��Ҫ�����½�����
fill_extent=dem_fill_des.extent.split(" ")
#��������Con()��������if�ṹ����down_slp_ang�ļ���
gp.MultiOutputMapAlgebra_sa("down_slp_ang = con(flowdir_out == 64 , "+str(deg)+" * atan(( dem_fill_b - SHIFT("+"dem_fill_b"+","+fill_extent[0]+","+StoS(fill_extent[1],cell_size,-1)+")) / "+str(cellorth)+"), con(flowdir_out == 128 , "+str(deg)+" * atan(( dem_fill_b - SHIFT("+"dem_fill_b"+","+StoS(fill_extent[0],cell_size,-1)+","+StoS(fill_extent[1],cell_size,-1)+")) / "+str(celldiag)+"), con(flowdir_out == 1 , "+str(deg)+" * atan(( dem_fill_b - SHIFT("+"dem_fill_b"+","+StoS(fill_extent[0],cell_size,-1)+","+fill_extent[1]+")) / "+str(cellorth)+"), con(flowdir_out == 2 , "+str(deg)+" * atan(( dem_fill_b - SHIFT("+"dem_fill_b"+","+StoS(fill_extent[0],cell_size,-1)+","+StoS(fill_extent[1],cell_size,1)+")) / "+str(celldiag)+"), con(flowdir_out == 4 , "+str(deg)+" * atan(( dem_fill_b - SHIFT("+"dem_fill_b"+","+fill_extent[0]+","+StoS(fill_extent[1],cell_size,1)+")) / "+str(cellorth)+"), con(flowdir_out == 8 , "+str(deg)+" * atan(( dem_fill_b - SHIFT("+"dem_fill_b"+","+StoS(fill_extent[0],cell_size,1)+","+StoS(fill_extent[1],cell_size,1)+")) / "+str(celldiag)+"), con(flowdir_out == 16 , "+str(deg)+" * atan(( dem_fill_b - SHIFT("+"dem_fill_b"+","+StoS(fill_extent[0],cell_size,1)+","+fill_extent[1]+")) / "+str(cellorth)+"), con(flowdir_out == 32 , "+str(deg)+" * atan(( dem_fill_b - SHIFT("+"dem_fill_b"+","+StoS(fill_extent[0],cell_size,1)+","+StoS(fill_extent[1],cell_size,-1)+")) / "+str(celldiag)+"), 0.1 ) ) ) ) ) ) ) )")
#������0.0�ĸ�����ֵΪ0.1
if gp.Exists("down_slp_ang2"):
    gp.Delete_management("down_slp_ang2")
gp.MultiOutputMapAlgebra_sa("down_slp_ang2 = con(down_slp_ang == 0 , 0.1 , down_slp_ang)")
gp.Delete_management("down_slp_ang")
gp.rename_management("down_slp_ang2","down_slp_ang")
#�������û�����ExtentΪԭʼ��С�����ü�downslope������������Ϊԭʼ����
gp.Extent="MAXOF"
gp.Extent=extent_nor
if gp.Exists("down_slp_ang2"):
    gp.Delete_management("down_slp_ang2")
gp.MultiOutputMapAlgebra_sa("down_slp_ang2 = down_slp_ang")
gp.Delete_management("down_slp_ang")
gp.rename_management("down_slp_ang2","down_slp_ang")

sendmsg("����ÿ�������ķ��ۼƸ����³�slp_lgth_cell�����ǵ�ֱ�ǻ�Խ�������������û���Ǿֲ��̵߳㣩")
if gp.Exists("slp_lgth_cell"):
    gp.Delete_management("slp_lgth_cell")
gp.MultiOutputMapAlgebra_sa("slp_lgth_cell = con(flowdir_out == 2 or flowdir_out == 8 or flowdir_out == 32 or flowdir_out == 128 , "+str(celldiag)+","+str(cellorth)+")")

#�����û�����ExtentΪ���巶Χ�������������Ϊ0�������������
gp.Extent="MAXOF"
gp.Extent=extent_buf
if gp.Exists("flowdir_out_b"):
    gp.Delete_management("flowdir_out_b")
gp.MultiOutputMapAlgebra_sa("flowdir_out_b = con(isnull(flowdir_out) , 0 ,flowdir_out)")
gp.Delete_management("flowdir_out")
#������ʼÿ��������Ԫ�ķ��ۼ��³���NCSL��������flowdir_in��flowdir_out����λ�����㣬�ҵ��������������������ΪNodata��Ȼ�����ߵ㣨���������ݵأ�Ϊ1/2*slp_lgth_cell���ȡ�
sendmsg("������ʼ�ۼ��³�����slp_lgth_cum")
if gp.Exists("slp_lgth_cum"):
    gp.Delete_management("slp_lgth_cum")
gp.MultiOutputMapAlgebra_sa("slp_lgth_cum=con((((flowdir_in && 64) and (SHIFT(flowdir_out_b,"+fill_extent[0]+","+str(float(fill_extent[1])-cell_size)+") == 4)) or ((flowdir_in && 128) and (SHIFT(flowdir_out_b,"+str(float(fill_extent[0])-cell_size)+","+str(float(fill_extent[1])-cell_size)+") == 8)) or ((flowdir_in && 1) and (SHIFT(flowdir_out_b,"+str(float(fill_extent[0])-cell_size)+","+fill_extent[1]+") == 16)) or ((flowdir_in && 2) and (SHIFT(flowdir_out_b,"+str(float(fill_extent[0])-cell_size)+","+str(float(fill_extent[1])+cell_size)+") == 32)) or ((flowdir_in && 4) and (SHIFT(flowdir_out_b,"+fill_extent[0]+","+str(float(fill_extent[1])+cell_size)+") == 64)) or ((flowdir_in && 8) and (SHIFT(flowdir_out_b,"+str(float(fill_extent[0])+cell_size)+","+str(float(fill_extent[1])+cell_size)+") == 128)) or ((flowdir_in && 16) and (SHIFT(flowdir_out_b,"+str(float(fill_extent[0])+cell_size)+","+fill_extent[1]+") == 1)) or ((flowdir_in && 32) and (SHIFT(flowdir_out_b,"+str(float(fill_extent[0])+cell_size)+","+str(float(fill_extent[1])-cell_size)+") == 2))), SETNULL(1 == 1) , 0.5 * slp_lgth_cell)")
#������ʼ�³�����㣨�ߵ�������ݵأ����������������³��Ѿ�����������ÿ����������ʼ�㽫��һ������1/2�����³���ֵ����ʼ��(�ֲ��̵߳�)������Χû������������Ԫ���룬����������Ԫ���룬����������Ԫ֮���½�Ϊ��ĸ�����Ԫ����Ӧ��DEM�е�ɽ����ɽ�����ϵĵ㼰λ��DEM��Ե�ĵ㣬��Щ��ͨ��ˮ���������ʶ��ʶ��������Ǹ�����Ԫ�ܱ߸����ڵ��ˮ���������֪��õ�Ԫ����������ǰ�Ĵ��룬�ı��ˡ�ƽ�ء��ߵ�õ�һ��0~1/2�����³���ֵ���µļ����ǣ���С�ۼ��³���1/2�����³�����ʹ������ݵغ͡�ƽ�ء��ߵ㣬�Ӷ�ȷ��ÿ������LS���ӵ�ֵ>0.00
sendmsg("������ʼ�³������slp_lgth_beg")
if gp.Exists("slp_lgth_beg"):
    gp.Delete_management("slp_lgth_beg")
gp.MultiOutputMapAlgebra_sa("slp_lgth_beg = con(isnull(slp_lgth_cum),"+str(cell_size)+",slp_lgth_cum)")
#ָ���¶Ƚ�����slope-end���������ۼ��³�����������������ǰ�Ĵ���������RUSLE׼������¶��ٽ�5%(2.8624����)������������ͬ����ʴ/�������ر�С���ر𶸵��¶ȣ���<5%ʹ�õĲ�����>=5%�Ĵ����ʹ��ǳ̲�������׽�����ʴ����ʼ�������̣����磬һ�����ߵ��ٽ�ֵ��ζ����Ҫ���ٵ��¶Ƚ��;Ϳ��Խ����ۼơ�
sendmsg("���������³��ۼ���ֵ�ĸ���slp_lgth_fac")
if gp.Exists("slp_end_fac"):
    gp.Delete_management("slp_end_fac")
gp.MultiOutputMapAlgebra_sa("slp_end_fac = con(down_slp_ang < 2.8624, "+str(scf_lt5)+" ,"+str(scf_ge5)+")")
#�Ƴ������κ�ʣ��ķ���������ݣ�֮ǰ�������µģ�
if gp.Exists("fromcell_n"):
    gp.Delete_management("fromcell_n")
if gp.Exists("fromcell_ne"):
    gp.Delete_management("fromcell_ne")
if gp.Exists("fromcell_e"):
    gp.Delete_management("fromcell_e")
if gp.Exists("fromcell_se"):
    gp.Delete_management("fromcell_se")
if gp.Exists("fromcell_s"):
    gp.Delete_management("fromcell_s")
if gp.Exists("fromcell_sw"):
    gp.Delete_management("fromcell_sw")
if gp.Exists("fromcell_w"):
    gp.Delete_management("fromcell_w")
if gp.Exists("fromcell_nw"):
    gp.Delete_management("fromcell_nw")
#������ǰ�汾�����д���һϵ�в���nodata�������������й��̣��������û���ExtentΪ��������dem_fill������Ϊ��Ĥ���黺�����
gp.Extent="MAXOF"
gp.Extent=extent_nor
gp.Mask=dem_input
gp.CellSize=cell_size
ndcell=1
#��������ǰ�汾���������õ�����nodata����Ϊ0
if gp.Exists("slp_lgth_nd2"):
    gp.Delete_management("slp_lgth_nd2")
gp.MultiOutputMapAlgebra_sa("slp_lgth_nd2 = 0")
warn=0
#��ʼΪÿ�����������ۼ��³��ĵ���ѭ�������ݸ�����Ԫ���򣬽����뵱ǰ������Ԫ�����θ�����Ԫ���ۼ��³������ۼӡ������ǰ������Ԫ�����ε�Ԫ��֪һ������ȡ��ǰ������Ԫ��������³�ֵ��Ϊ��ǰ������Ԫ�������ۼ��³���
finished=0
n=1
while not finished:
    sendmsg("���ڿ�ʼÿ�������³�����ĵ�"+str(n)+"��ѭ����")
    if gp.Exists("slp_lgth_prev"):
        gp.Delete_management("slp_lgth_prev")
    gp.MultiOutputMapAlgebra_sa("slp_lgth_prev = slp_lgth_cum")
    count=range(1,9)
    for counter in count:
        #Ϊ��ͬ���������ò�ͬ�Ĳ���ֵ
        if counter==1:
            dirfrom=4
            dirpossto=64
            cellcol=0
            cellrow=-1
        elif counter==2:
            gp.rename_management("fromcell_dir","fromcell_n")
            dirfrom=8
            dirpossto=128
            cellcol=1
            cellrow=-1
        elif counter==3:
            gp.rename_management("fromcell_dir","fromcell_ne")
            dirfrom=16
            dirpossto=1
            cellcol=1
            cellrow=0
        elif counter==4:
            gp.rename_management("fromcell_dir","fromcell_e")
            dirfrom=32
            dirpossto=2
            cellcol=1
            cellrow=1
        elif counter==5:
            gp.rename_management("fromcell_dir","fromcell_se")
            dirfrom=64
            dirpossto=4
            cellcol=0
            cellrow=1
        elif counter==6:
            gp.rename_management("fromcell_dir","fromcell_s")
            dirfrom=128
            dirpossto=8
            cellcol=-1
            cellrow=1
        elif counter==7:
            gp.rename_management("fromcell_dir","fromcell_sw")
            dirfrom=1
            dirpossto=16
            cellcol=-1
            cellrow=0
        else:
            gp.rename_management("fromcell_dir","fromcell_w")
            dirfrom=2
            dirpossto=32
            cellcol=-1
            cellrow=-1
        #gp.MultiOutputMapAlgebra_sa("fromcell_dir=con((^(flowdir_in && "+str(dirpossto)+")) or (SHIFT(flowdir_out_b,"+StoS(fill_extent[0],cell_size,-1*cellcol)+","+StoS(fill_extent[1],cell_size,cellrow)+") ^= "+str(dirfrom)+") or (down_slp_ang < (SHIFT(down_slp_ang,"+StoS(fill_extent[0],cell_size,-1*cellcol)+","+StoS(fill_extent[1],cell_size,cellrow)+") * slp_end_fac)) , 0 , con(down_slp_ang >= (SHIFT(down_slp_ang,"+StoS(fill_extent[0],cell_size,-1*cellcol)+","+StoS(fill_extent[1],cell_size,cellrow)+") * slp_end_fac ) , SHIFT(slp_lgth_prev,"+StoS(fill_extent[0],cell_size,-1*cellcol)+","+StoS(fill_extent[1],cell_size,cellrow)+") + SHIFT(slp_lgth_cell,"+StoS(fill_extent[0],cell_size,-1*cellcol)+","+StoS(fill_extent[1],cell_size,cellrow)+") , con(isnull(SHIFT(slp_lgth_prev,"+StoS(fill_extent[0],cell_size,-1*cellcol)+","+StoS(fill_extent[1],cell_size,cellrow)+")), setnull(1 == 1) , 0)))")
        gp.MultiOutputMapAlgebra_sa("fromcell_dir=con((^(flowdir_in && "+str(dirpossto)+")) or (SHIFT(flowdir_out_b,"+StoS(extent[0],cell_size,-1*cellcol)+","+StoS(extent[1],cell_size,cellrow)+") ^= "+str(dirfrom)+") or (down_slp_ang < (SHIFT(down_slp_ang,"+StoS(extent[0],cell_size,-1*cellcol)+","+StoS(extent[1],cell_size,cellrow)+") * slp_end_fac)) , 0 , con(down_slp_ang >= (SHIFT(down_slp_ang,"+StoS(extent[0],cell_size,-1*cellcol)+","+StoS(extent[1],cell_size,cellrow)+") * slp_end_fac ) , SHIFT(slp_lgth_prev,"+StoS(extent[0],cell_size,-1*cellcol)+","+StoS(extent[1],cell_size,cellrow)+") + SHIFT(slp_lgth_cell,"+StoS(extent[0],cell_size,-1*cellcol)+","+StoS(extent[1],cell_size,cellrow)+") , con(isnull(SHIFT(slp_lgth_prev,"+StoS(extent[0],cell_size,-1*cellcol)+","+StoS(extent[1],cell_size,cellrow)+")), setnull(1 == 1) , 0)))")
        if counter==8:
            gp.rename_management("fromcell_dir","fromcell_nw")
    #��fromcell��������ѡ�������ۼ��³�ֵ
    if gp.Exists("slp_lgth_cum"):
        gp.Delete_management("slp_lgth_cum")
    gp.MultiOutputMapAlgebra_sa("slp_lgth_cum = max(fromcell_n, fromcell_ne, fromcell_e, fromcell_se, fromcell_s, fromcell_sw, fromcell_w, fromcell_nw, slp_lgth_beg)")
    #������һ��ѭ�����и�������ֵ
    nodata=ndcell
    if nodata == 0:
        fanished=1
    #�����������nodata����
    if gp.exists("slp_lgth_nd"):
        gp.Delete_management("slp_lgth_nd")
    gp.MultiOutputMapAlgebra_sa("slp_lgth_nd = con((isnull(slp_lgth_cum) and (^ isnull(flowdir_out_b))), 1 , 0)")
    ndcell=0
    #��ȡslp_lgth_nd�����ֵ��ndcell
    try:
        ndcell=int(gp.getrasterproperties_management("slp_lgth_nd","MAXIMUM"))
        sendmsg(str(ndcell))
    except:
        sendmsg(gp.GetMessages(2))
    
    #��������ǰ�汾�м���ÿ��ѭ����nodata�����Ƿ������ӣ��������ѭ����û�����ӣ������ѭ����ʼ����LS����������������£��п���һ��������С��nodata���������ڱ߽磬����������DEM����10�������������ڣ�������ʵ���о������ڡ�
    if gp.Exists("nd_chg2"):
        gp.Delete_management("nd_chg2")
    gp.MultiOutputMapAlgebra_sa("nd_chg2 = con((slp_lgth_nd == slp_lgth_nd2) , 0 , 1)")
    ndchg2=0
    try:
        ndchg2=int(gp.getrasterproperties_management("nd_chg2","MAXIMUM"))
        sendmsg(str(ndchg2))
    except:
        sendmsg(gp.GetMessages(2))
    nd2=ndchg2
    if nd2 == 0:
        finished=1
        warn=1
    #ɾ����һ��ѭ������ʱ���������
    gp.Delete_management("fromcell_n")
    gp.Delete_management("fromcell_ne")
    gp.Delete_management("fromcell_e")
    gp.Delete_management("fromcell_se")
    gp.Delete_management("fromcell_s")
    gp.Delete_management("fromcell_sw")
    gp.Delete_management("fromcell_w")
    gp.Delete_management("fromcell_nw")

    if gp.Exists("slp_lgth_nd2"):
        gp.Delete_management("slp_lgth_nd2")
    gp.MultiOutputMapAlgebra_sa("slp_lgth_nd2 = slp_lgth_nd")
    gp.Delete_management("slp_lgth_nd")
    n=n+1

#�����һ��ѭ���������ۼƸ���������Ϊmax���ü�������������ȥ
gp.rename_management("slp_lgth_cum","slp_lgth_max")
gp.Extent="MAXOF"
gp.Extent=extent_nor
if gp.Exists("slp_lgth_max2"):
    gp.Delete_management("slp_lgth_max2")
gp.rename_management("slp_lgth_max","slp_lgth_max2")
gp.MultiOutputMapAlgebra_sa("slp_lgth_max = slp_lgth_max2")
gp.Delete_management("slp_lgth_max2")

#����б�Ҫ�Ļ����³���λ��metersת��Ϊfeet
if gp.Exists("slp_lgth_ft"):
    gp.Delete_management("slp_lgth_ft")
if demunits == "meters":
    gp.MultiOutputMapAlgebra_sa("slp_lgth_ft = slp_lgth_max / 0.3048")
else:
    gp.MultiOutputMapAlgebra_sa("slp_lgth_ft = slp_lgth_max")
#��������ǰ�汾�и���ϸ��/ϸ����ʴ��ΪRUSLE���³�����ָ����Ҫ��ȷ���ǲݵ�/ɭ���е͵����жȣ�����McCool����׼���б��4-5��1997����
sendmsg("�����¶���ָ��m_slpexp")
if gp.Exists("m_slpexp"):
    gp.Delete_management("m_slpexp")
gp.MultiOutputMapAlgebra_sa("m_slpexp=con(down_slp_ang <= 0.1 , 0.01 ,con((down_slp_ang > 0.1) and (down_slp_ang < 0.2) , 0.02, con((down_slp_ang >= 0.2) and (down_slp_ang < 0.4), 0.04, con((down_slp_ang >= 0.4) and (down_slp_ang < 0.85), 0.08, con((down_slp_ang >= 0.85) and (down_slp_ang < 1.4) , 0.14, con((down_slp_ang >= 1.4) and (down_slp_ang < 2.0) , 0.18, con((down_slp_ang >= 2.0) and (down_slp_ang < 2.6), 0.22, con((down_slp_ang >= 2.6) and (down_slp_ang < 3.1), 0.25, con((down_slp_ang >= 3.1 ) and (down_slp_ang < 3.7), 0.28, con((down_slp_ang >= 3.7 ) and (down_slp_ang < 5.2), 0.32, con((down_slp_ang >= 5.2) and (down_slp_ang < 6.3), 0.35, con((down_slp_ang >= 6.3) and (down_slp_ang < 7.4), 0.37, con((down_slp_ang >= 7.4) and (down_slp_ang < 8.6), 0.40, con((down_slp_ang >= 8.6) and (down_slp_ang < 10.3), 0.41, con((down_slp_ang >= 10.3) and (down_slp_ang < 12.9), 0.44, con((down_slp_ang >= 12.9) and (down_slp_ang < 15.7), 0.47, con((down_slp_ang >= 15.7) and (down_slp_ang < 20.0), 0.49, con((down_slp_ang >= 20.0) and (down_slp_ang < 25.8), 0.52, con((down_slp_ang >= 25.8) and (down_slp_ang < 31.5), 0.54, con((down_slp_ang >= 31.5) and (down_slp_ang < 37.2), 0.55, 0.56))))))))))))))))))))")#��������ǰ�汾������L����ʱ�����³�����72.6
sendmsg("����L����")
if gp.Exists(dem_input+"_ruslel"):
    gp.Delete_management(dem_input+"_ruslel")
gp.MultiOutputMapAlgebra_sa(dem_input+"_ruslel = pow(( slp_lgth_ft / 72.6 ), m_slpexp )")
#��������ǰUSLE���룬���濪ʼ����S����
sendmsg("����S����")
if gp.Exists(dem_input+"_rusles"):
    gp.Delete_management(dem_input+"_rusles")
gp.MultiOutputMapAlgebra_sa(dem_input+"_rusles = con(down_slp_ang >= 5.1428 , 16.8 * (sin(down_slp_ang / "+str(deg)+")) - 0.50 , 10.8 * (sin(down_slp_ang / "+str(deg)+")) + 0.03)")

#��L���Ӻ�S������ˣ��õ�LS���ӵ�ֵ��Ȼ��������ü�֮����.vat���ͳ�Ʒ�����������ֵ����100��Ϊ����ļ���ౣ����Ҫ�����֡�
sendmsg("�����������Χ�ڵ�LSֵ")
wshed_des=gp.describe(wshed)
extent_wshed=wshed_des.Extent
sendmsg( "����߽�Ϊ��"+extent_wshed)
gp.Extent=extent_wshed
gp.Mask=wshed
if gp.Exists(dem_input+"_ruslels2"):
    gp.Delete_management(dem_input+"_ruslels2")
gp.MultiOutputMapAlgebra_sa(dem_input+"_ruslels2 = int((("+dem_input+"_ruslel * "+dem_input+"_rusles) * 100) + 0.5)")
