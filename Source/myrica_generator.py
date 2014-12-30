#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# Author: Tomokuni SEKIYA
#
# This script is for generating ``myrica'' font
#
# * Inconsolata  : Inconsolata-Regular.ttf            : 1.013 (Google Fonts)
# * 源真ゴシック : GenShinGothic-Monospace-Light.ttf  : 1.058.20140828
# * (original)   : ReplaceParts.ttf                   : 1.006.20141102
# * (original)   : HintingParts.ttf                   : 2.001.20141221
#
# 以下のように構成されます。
# ・英数字記号は、Inconsolata
# ・他の文字は、源真ゴシック
# ・一部の文字を視認性向上のため、源真ゴシックをベースに migu の特徴を取込み
#     半濁点（ぱぴぷぺぽパピプペポ の右上の円）を大きくして、濁点と判別しやすく
#     「カ力 エ工 ロ口 ー一 ニ二」（カタカナ・漢字）の区別
#     ～〜（FULLWIDTH TILDE・WAVE DASH）の区別

# version
newfont_version      = "2.002.20141230"
newfont_sfntRevision = 0x00010000

# set font name
newfontM  = ("../Work/MyricaM.ttf", "MyricaM", "Myrica M", "Myrica Monospace")
newfontP  = ("../Work/MyricaP.ttf", "MyricaP", "Myrica P", "Myrica Proportional")
newfontN  = ("../Work/MyricaN.ttf", "MyricaN", "Myrica N", "Myrica Narrow")

# source file
srcfontIncosolata   = "../SourceTTF/Inconsolata-Regular.ttf"
srcfontGenShin      = "../SourceTTF/GenShinGothic-Monospace-Light-ExpandH20.ttf"
srcfontReplaceParts = "ReplaceParts.ttf"
srcfontHintingParts = "HintingParts.ttf"

# out file
outfontNoHint = "../Work/MyricaM_NoHint.ttf"

# flag
scalingDownIfWidth_flag = True

# set ascent and descent (line width parameters)
newfont_ascent  = 840
newfont_descent = 184
newfont_em = newfont_ascent + newfont_descent

newfont_winAscent   = 840
newfont_winDescent  = 170
newfont_typoAscent  = newfont_winAscent
newfont_typoDescent = -newfont_winDescent
newfont_typoLinegap = 0
newfont_hheaAscent  = newfont_winAscent
newfont_hheaDescent = -newfont_winDescent
newfont_hheaLinegap = 0

# define
generate_flags = ('opentype', 'PfEd-lookups', 'TeX-table')
panoseBase = (2, 11, 5, 9, 2, 2, 3, 2, 2, 7)

########################################
# setting
########################################

import copy
import os
import sys
import shutil
import fontforge
import psMat

# 縦書きのために指定する
fontforge.setPrefs('CoverageFormatsAllowed', 1)
# 大変更時に命令を消去 0:オフ 1:オン
fontforge.setPrefs('ClearInstrsBigChanges', 0)
# TrueType命令をコピー 0:オフ 1:オン
fontforge.setPrefs('CopyTTFInstrs', 1)

########################################
# pre-process
########################################

print 
print 
print "myrica generator " + newfont_version
print 
print "This script is for generating 'myrica' font"
print 
if os.path.exists( srcfontIncosolata ) == False:
    print "Error: " + srcfontIncosolata + " not found"
    sys.exit( 1 )
if os.path.exists( srcfontReplaceParts ) == False:
    print "Error: " + srcfontReplaceParts + " not found"
    sys.exit( 1 )
if os.path.exists( srcfontGenShin ) == False:
    print "Error: " + srcfontGenShin + " not found"
    sys.exit( 1 )

########################################
# define function
########################################
def matRescale(origin_x, origin_y, scale_x, scale_y):
    return psMat.compose(
        psMat.translate(-origin_x, -origin_y), psMat.compose(
        psMat.scale(scale_x, scale_y), 
        psMat.translate(origin_x, origin_y)))

def matMove(move_x, move_y):
    return psMat.translate(move_x, move_y)

def rng(start, end):
    return range(start, end + 1)

def flatten(iterable):
    it = iter(iterable)
    for e in it:
        if isinstance(e, (list, tuple)):
            for f in flatten(e):
                yield f
        else:
            yield e

def select(font, *codes):
    font.selection.none()
    selectMore(font, codes)

def selectMore(font, *codes):
    flat = flatten(codes)
    for c in flat:
        if isinstance(c, (unicode, )):
            font.selection.select(("more",), ord(c))
        else:
            font.selection.select(("more",), c)

def selectLess(font, *codes):
    flat = flatten(codes)
    for c in flat:
        if isinstance(c, (unicode, )):
            font.selection.select(("less",), ord(c))
        else:
            font.selection.select(("less",), c)

def selectExistAll(font):
    font.selection.none()
    for glyphName in font:
        if font[glyphName].isWorthOutputting() == True:
            font.selection.select(("more",), glyphName)

def copyAndPaste(srcFont, srcCodes, dstFont, dstCodes):
    select(srcFont, srcCodes)
    srcFont.copy()
    select(dstFont, dstCodes)
    dstFont.paste()

def copyAndPasteInto(srcFont, srcCodes, dstFont, dstCodes, pos_x, pos_y):
    select(srcFont, srcCodes)
    srcFont.copy()
    select(dstFont, dstCodes)
    dstFont.transform(matMove(-pos_x, -pos_y))
    dstFont.pasteInto()
    dstFont.transform(matMove(pos_x, pos_y))

def scalingDownIfWidth(font, scaleX, scaleY):
    for glyph in font.selection.byGlyphs:
        width = glyph.width
        glyph.transform(matRescale(width / 2, 0, scaleX, scaleY))
        glyph.width = width

def centerInWidth(font):
    for glyph in font.selection.byGlyphs:
        w  = glyph.width
        wc = w / 2
        bb = glyph.boundingBox()
        bc = (bb[0] + bb[2]) / 2
        glyph.transform(matMove(wc - bc, 0))
        glyph.width = w

def setWidth(font, width):
    for glyph in font.selection.byGlyphs:
        glyph.width = width

def setAutoWidthGlyph(glyph, separation):
    bb = glyph.boundingBox()
    bc = (bb[0] + bb[2]) / 2
    nw = (bb[2] - bb[0]) + separation * 2
    if glyph.width > nw:
        wc = nw / 2
        glyph.transform(matMove(wc - bc, 0))
        glyph.width = nw

def autoHintAndInstr(font, *codes):
    removeHintAndInstr(font, codes)
    font.autoHint()
    font.autoInstr()

def removeHintAndInstr(font, *codes):
    select(font, codes)
    for glyph in font.selection.byGlyphs:
        if glyph.isWorthOutputting() == True:
            glyph.manualHints = False
            glyph.ttinstrs = ()
            glyph.dhints = ()
            glyph.hhints = ()
            glyph.vhints = ()

def copyTti(srcFont, dstFont):
    for glyphName in dstFont:
        dstFont.setTableData('fpgm', srcFont.getTableData('fpgm'))
        dstFont.setTableData('prep', srcFont.getTableData('prep'))
        dstFont.setTableData('cvt',  srcFont.getTableData('cvt'))
        dstFont.setTableData('maxp', srcFont.getTableData('maxp'))
        copyTtiByGlyphName(srcFont, dstFont, glyphName)

def copyTtiByGlyphName(srcFont, dstFont, glyphName):
    try:
        dstGlyph = dstFont[glyphName]
        srcGlyph = srcFont[glyphName]
        if srcGlyph.isWorthOutputting() == True and dstGlyph.isWorthOutputting() == True:
            dstGlyph.manualHints = True
            dstGlyph.ttinstrs = srcFont[glyphName].ttinstrs
            dstGlyph.dhints = srcFont[glyphName].dhints
            dstGlyph.hhints = srcFont[glyphName].hhints
            dstGlyph.vhints = srcFont[glyphName].vhints
    except TypeError:
        pass

def setFontProp(font, fontInfo):
    font.fontname   = fontInfo[1]
    font.familyname = fontInfo[2]
    font.fullname   = fontInfo[3]
    font.weight = "Book"
    font.copyright =  "Copyright (c) 2006-2012 Raph Levien (Inconsolata)\n"
    font.copyright += "Copyright (c) 2013 M+ FONTS PROJECT (M+)\n"
    font.copyright += "Copyright (c) 2013 itouhiro (Migu)\n"
    font.copyright += "Copyright (c) 2014 MM (Mgen+)\n"
    font.copyright += "Copyright (c) 2014 Adobe Systems Incorporated. (NotoSansJP)\n"
    font.copyright += "Licenses:\n"
    font.copyright += "SIL Open Font License Version 1.1 "
    font.copyright += "(http://scripts.sil.org/ofl)\n"
    font.copyright += "Apache License, Version 2.0 "
    font.copyright += "(http://www.apache.org/licenses/LICENSE-2.0)"
    font.version = newfont_version
    font.sfntRevision = newfont_sfntRevision
    font.sfnt_names = (('English (US)', 'UniqueID', fontInfo[2]), )
    #('Japanese', 'PostScriptName', fontInfo[2]), 
    #('Japanese', 'Family', fontInfo[1]), 
    #('Japanese', 'Fullname', fontInfo[3]), 

    font.hasvmetrics = True
    font.head_optimized_for_cleartype = True

    font.os2_panose = panoseBase
    font.os2_vendor = "M+"
    font.os2_version = 1

    font.os2_winascent       = newfont_winAscent
    font.os2_winascent_add   = 0
    font.os2_windescent      = newfont_winDescent
    font.os2_windescent_add  = 0
    font.os2_typoascent      = newfont_typoAscent
    font.os2_typoascent_add  = 0
    font.os2_typodescent     = -newfont_typoDescent
    font.os2_typodescent_add = 0
    font.os2_typolinegap     = newfont_typoLinegap
    font.hhea_ascent         = newfont_hheaAscent
    font.hhea_ascent_add     = 0
    font.hhea_descent        = -newfont_hheaDescent
    font.hhea_descent_add    = 0
    font.hhea_linegap        = newfont_hheaLinegap

charASCII  = rng(0x0021, 0x007E)
charZHKana = list(u"ぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわゐゑをん"),
charZKKana = list(u"ァアィイゥウェエォオカガキギクグケゲコゴサザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロヮワヰヱヲンヴヵヶ"),
charHKKana = list(u"､｡･ｰﾞﾟ｢｣ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜｦﾝｧｨｩｪｫｬｭｮｯ")
charZEisu = list(u"０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ")

########################################
# modified Inconsolata
########################################

print
print "Open " + srcfontIncosolata
fIn = fontforge.open( srcfontIncosolata )

# modify
print "modify"
# 拡大 "'`
select(fIn, 0x0022, 0x0027, 0x0060)
fIn.transform(matRescale(250, 600, 1.15, 1.15))
setWidth(fIn, 1000 / 2)

# 拡大 ,.:;
select(fIn, 0x002c, 0x002e, 0x003a, 0x003b)
fIn.transform(matRescale(250, 0, 1.20, 1.20))
setWidth(fIn, 1000 / 2)

# 移動 ~
select(fIn, 0x007e)
fIn.transform(matMove(0, 120))

# 移動 ()
select(fIn, list(u"()"))
fIn.transform(matMove(0, 89))

# 移動 []
select(fIn, list(u"[]"))
fIn.transform(matMove(0, 15))

# 移動 {}
select(fIn, list(u"{}"))
fIn.transform(matMove(0, 91))

# | -> broken | (Inconsolata's glyph)
copyAndPaste(fIn, 0x00a6, fIn, 0x007c)
select(fIn, 0x007c)
fIn.transform(matMove(0, 100))

# D -> D of Eth (D with cross-bar)
copyAndPaste(fIn, 0x0110, fIn, 0x0044)

# r -> r of serif (Inconsolata's unused glyph)
copyAndPaste(fIn,  65548, fIn, 0x0072)

# 必要文字(半角英数字記号)だけを残して削除
select(fIn, rng(0x0021, 0x007E))
fIn.selection.invert()
fIn.clear()

# modify em
fIn.em  = newfont_em
fIn.ascent  = newfont_ascent
fIn.descent = newfont_descent

#setWidth(fIn, newfont_em / 2)

fIn.selection.all()
fIn.round()

#fIn.generate("../Work/modIncosolata.ttf", '', generate_flags)

########################################
# modified ReplaceParts
########################################

print
print "Open " + srcfontReplaceParts
fRp = fontforge.open( srcfontReplaceParts )

# modify em
fRp.em  = newfont_em
fRp.ascent  = newfont_ascent
fRp.descent = newfont_descent

# marge ReplaceParts
print "marge ReplaceParts to Incosolata"
# 文字の置換え
target = (
    0x002a,  # * : astarisk
    0x006c,  # l : small letter l
    0x2013,  # – : en dash –
    0x2014)  # — : em dash —
copyAndPaste(fRp, target, fIn, target)

# post-process
fRp.selection.all()
fRp.round()

#fRp.generate("../Work/modReplaceParts.ttf", '', generate_flags)
fRp.close()

########################################
# modified GenShin
########################################

print
print "Open " + srcfontGenShin
fGj = fontforge.open( srcfontGenShin )

# modify em
fGj.em  = newfont_em
fGj.ascent  = newfont_ascent
fGj.descent = newfont_descent

# modify
print "modify"

# 半角英数字記号を削除
select(fIn, rng(0x0021, 0x007E))
fGj.clear()

# scaling down
if scalingDownIfWidth_flag == True:
    print "While scaling, wait a little..."
    # 0.91はRictyに準じた。
    selectExistAll(fGj)
    selectLess(fGj, (charASCII, charHKKana, charZHKana, charZKKana, charZEisu))
    scalingDownIfWidth(fGj, 0.91, 0.91)
    # 平仮名/片仮名のサイズを調整
    select(fGj, (charZHKana,charZKKana))
    scalingDownIfWidth(fGj, 0.97, 0.97)
    # 全角英数の高さを調整 (半角英数の高さに合わせる)
    select(fGj, charZEisu)
    scalingDownIfWidth(fGj, 0.91, 0.86)

#fGj.generate("../Work/modGenShin.ttf", '', generate_flags)

########################################
# create MyricaM
########################################
fMm = fIn

print
print "Build " + newfontM[0]

# pre-process
setFontProp(fMm, newfontM)

# marge Mgen+
print "marge GenShin"
# マージ
fMm.mergeFonts( srcfontGenShin )
fMm.os2_unicoderanges = fGj.os2_unicoderanges
fMm.os2_codepages = fGj.os2_codepages
# ルックアップテーブルの置換え
for l in fGj.gsub_lookups:
    fMm.importLookups(fGj, l)
for l in fMm.gsub_lookups:
    if l.startswith(fGj.fontname + "-") == True:
        fMm.removeLookup(l)
#for l in fMm.gpos_lookups:
#    fMm.removeLookup(l)
#for l in fGj.gpos_lookups:
#   fMm.importLookups(fGj, l)

# post-process
fMm.selection.all()
fMm.round()

# generate
print "Generate " + newfontM[0]
fMm.generate(newfontM[0], '', generate_flags)

# marge HinthingParts
if os.path.exists( srcfontHintingParts ) == True:
    print "marge HintingParts"
    shutil.copyfile(newfontM[0], outfontNoHint)
    fHp = fontforge.open( srcfontHintingParts )

    #property
    setFontProp(fHp, newfontM)

    # modify em
    fHp.em  = newfont_em
    fHp.ascent  = newfont_ascent
    fHp.descent = newfont_descent

    # delete
    for glyph in fHp.glyphs():
        if glyph.unicode <= 0:
            select(fHp, glyph.glyphname)
            fHp.clear()

    # marge
    fHp.mergeFonts( newfontM[0] )
    fHp.os2_unicoderanges = fMm.os2_unicoderanges
    fHp.os2_codepages = fMm.os2_codepages
    # ルックアップテーブルの置換え
    for l in fMm.gsub_lookups:
        fHp.importLookups(fMm, l)
    for l in fHp.gsub_lookups:
        if l.startswith(fMm.fontname + "-") == True:
            fHp.removeLookup(l)
#    for l in fHp.gpos_lookups:
#        fHp.removeLookup(l)
#    for l in fMm.gpos_lookups:
#       fHp.importLookups(fMm, l)

    # post-process
    fHp.selection.all()
    fHp.round()

    # generate
    print "Generate " + newfontM[0] + " with Hinting"
    fHp.generate(newfontM[0], '', generate_flags)
    fHp.close()

fMm.close()
fGj.close()

########################################
# create MyricaP
########################################
print
print "Build " + newfontP[0]
fMp = fontforge.open( newfontM[0] )

# pre-process
fMp.fontname   = newfontP[1]
fMp.familyname = newfontP[2]
fMp.fullname   = newfontP[3]
fMp.sfnt_names = (('English (US)', 'UniqueID', newfontP[2]), )

panose = list(fMp.os2_panose)
panose[3] = 0
fMp.os2_panose = tuple(panose)

# modify
print "modify"

# 全角
zenkaku = (60,)
# 半角
hankaku = (50,)

# 全文字の幅の自動設定
fMp.selection.all()
for glyph in fMp.selection.byGlyphs:
    #print glyph.glyphname + ", code " + str(glyph.unicode) + ", width " + str(glyph.width)
    if glyph.width == newfont_em:         # 全角文字
        setAutoWidthGlyph(glyph, zenkaku[0])
    else:                                 # 半角文字
        setAutoWidthGlyph(glyph, hankaku[0])

# 半角数字は幅固定で中央配置
select(fMp, rng(0x0030,0x0039))   # 0-9
setWidth(fMp, 490)
centerInWidth(fMp)

# スペース
select(fMp, 0x0020)   # 半角スペース
setWidth(fMp, 340)
centerInWidth(fMp)
select(fMp, 0x3000)   # 全角スペース
setWidth(fMp, 680)
centerInWidth(fMp)

# post-process
fMp.selection.all()
fMp.round()

# generate
print "Generate " + newfontP[0]
fMp.generate(newfontP[0], '', generate_flags)

fMp.close()

########################################
# create MyricaN
########################################
print
print "Build " + newfontN[0]
fMn = fontforge.open( newfontM[0] )

# pre-process
fMn.fontname   = newfontN[1]
fMn.familyname = newfontN[2]
fMn.fullname   = newfontN[3]
fMn.sfnt_names = (('English (US)', 'UniqueID', newfontN[2]), )

panose = list(fMn.os2_panose)
panose[3] = 0
fMn.os2_panose = tuple(panose)

# modify
print "modify"

# 半角英数
heisu = (0.68, 1.00, 50, (rng(0x0030,0x0039), rng(0x0041,0x005A), rng(0x0061,0x007A)))
# 半角記号
hkigo = (0.68, 1.00, 50, (rng(0x0021,0x002F), rng(0x003A,0x0040), rng(0x005B,0x0060), rng(0x007B,0x007E)))
# 全角かな
zkana = (0.55, 1.00, 50, rng(0x3041,0x31FF))
# 半角かな
hkana = (0.68, 1.00, 50, rng(0xFF66,0xFF9F))
# その他の全角文字
zetc  = (0.60, 1.00, 50)
# その他の半角文字
hetc  = (0.68, 1.00, 50)

# 拡大縮小 と 幅の自動設定
fMn.selection.all()
for glyph in fMn.selection.byGlyphs:
    #print glyph.glyphname + ", code " + str(glyph.unicode) + ", width " + str(glyph.width)
    glyph.ttinstrs = ()
    if glyph.unicode in zkana[3]:           # 全角かな
        glyph.transform(matRescale(0, 0, zkana[0], zkana[1]))
        setAutoWidthGlyph(glyph, zkana[2])
    elif glyph.width == newfont_em:         # その他の全角文字
        glyph.transform(matRescale(0, 0, zetc[0],  zetc[1]))
        setAutoWidthGlyph(glyph, zetc[2])
    else:                                   # 半角文字
        glyph.transform(matRescale(0, 0, hetc[0],  hetc[1]))
        bb = glyph.boundingBox()
        nw = (bb[2] - bb[0]) + hetc[2] * 2
        if glyph.width > nw:
            setAutoWidthGlyph(glyph, hetc[2])

# 半角数字は幅固定で中央配置
select(fMn, rng(0x0030,0x0039))   # 0-9
setWidth(fMn, 350)
centerInWidth(fMn)

# スペース
select(fMn, 0x0020)   # 半角スペース
setWidth(fMn, 350)
centerInWidth(fMn)
select(fMn, 0x3000)   # 全角スペース
setWidth(fMn, 500)
centerInWidth(fMn)

# post-process
fMn.selection.all()
fMn.round()

# generate
print "Generate " + newfontN[0]
fMn.generate(newfontN[0], '', generate_flags)

fMn.close()
