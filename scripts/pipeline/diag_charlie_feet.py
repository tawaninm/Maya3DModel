import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds
cmds.file(r"D:\projects\ProjectAnimation\scenes\Characters\Charlie_Mixamo.mb", open=True, force=True)
def w(n): return [round(v, 1) for v in cmds.xform(n, q=True, ws=True, t=True)]
print("L| bind joints: LeftFoot", w("mixamorig:LeftFoot"), "RightFoot", w("mixamorig:RightFoot"), "LeftToeBase", w("mixamorig:LeftToeBase"), "RightToeBase", w("mixamorig:RightToeBase"))
print("L| UpLeg", w("mixamorig:LeftUpLeg"), w("mixamorig:RightUpLeg"))
shoes = [m for m in cmds.ls(type="mesh", noIntermediate=True) if "shoe" in m.lower()]
print("L| shoe meshes", shoes)
for s in shoes:
    tr = cmds.listRelatives(s, parent=True)[0]
    xs = cmds.xform(s + ".vtx[*]", q=True, ws=True, t=True)
    px = xs[0::3]; py = xs[1::3]; pz = xs[2::3]
    n = len(px)
    cx = (max(px) + min(px)) / 2.0
    left = [i for i in range(n) if px[i] > 0]; right = [i for i in range(n) if px[i] <= 0]
    def rng(idx, arr): return (round(min(arr[i] for i in idx), 1), round(max(arr[i] for i in idx), 1)) if idx else None
    print("L|", tr, "verts", n, "x range", round(min(px), 1), round(max(px), 1), "| +x half x", rng(left, px), "-x half x", rng(right, px))
    print("L|   gap between halves near x=0: nearest +x vertex", round(min(px[i] for i in left), 2) if left else None, "nearest -x vertex", round(max(px[i] for i in right), 2) if right else None)
    sc = cmds.ls(cmds.listHistory(s), type="skinCluster")
    if sc:
        infl = cmds.skinCluster(sc[0], q=True, influence=True)
        k = len(infl)
        dom = {}
        wrong = 0
        for i in range(n):
            row = cmds.skinPercent(sc[0], tr + ".vtx[%d]" % i, q=True, value=True)
            j = infl[row.index(max(row))]
            dom[j] = dom.get(j, 0) + 1
            if (px[i] > 0 and "Right" in j) or (px[i] <= 0 and "Left" in j):
                wrong += 1
        print("L|   dominant influence counts", dom)
        print("L|   verts on one side dominated by the OTHER side's leg joint:", wrong, "of", n)
maya.standalone.uninitialize()
