#import numpy as np
#from omegaconf import DictConfig

# 對單字推導
# eg. input: target_chara_position = [['群', '微', '開', '三', '止', '平'], ['見', '微', '開', '三', '止', '平']]
#            target_chara = '幾', config = config
#     out  : [['k', 'ei', '4', 0, 0, 0], ['g', 'ei', '1', 0, 0, 0]]
def retrive_pron_by_position(target_chara_position: list, target_chara: str, config) -> list:
    target_chara_prons_set = set()
    target_chara_prons = []
    for i in target_chara_position:
        target_chara_m = change_tone_class(i, config.tone)
        target_chara_initial = retrive_initial_by_position(target_chara_m, config.initial)
        target_chara_final = retrive_final_by_position(target_chara_m, config.final)
        target_chara_tone = retrive_tone_by_position(target_chara_m, config.tone)
        target_chara_pron_split = [target_chara_initial[0], target_chara_final[0], target_chara_tone]
        target_chara_pron_split = adapt_final_versus_tone(target_chara_pron_split, i, config.tone)
        target_chara_pron = "".join(target_chara_pron_split)
        
        target_chara_mark_initial = 0
        if target_chara!="" and len(target_chara_initial) > 3 :
            if target_chara in target_chara_initial[1]: target_chara_mark_initial = 1
            if target_chara in target_chara_initial[2]: target_chara_mark_initial = 2
            if target_chara in target_chara_initial[3]: target_chara_mark_initial = 3
        target_chara_mark_final = 0
        if target_chara!="" and len(target_chara_final) > 3 :
            if target_chara in target_chara_final[1]: target_chara_mark_final = 1
            if target_chara in target_chara_final[2]: target_chara_mark_final = 2
            if target_chara in target_chara_final[3]: target_chara_mark_final = 3
        
        target_chara_mark = [
            target_chara_mark_initial,
            target_chara_mark_final,
            # 上面~十行可以縮短爲下面兩行，但要避免引入 numpy，所以算了
            #np.where([target_chara in i for i in [target_chara]+target_chara_initial[1:]])[0][-1], 
            #np.where([target_chara in i for i in [target_chara]+target_chara_final[1:]])[0][-1],
            0,
        ]
        if target_chara_pron not in target_chara_prons_set or any(target_chara_mark):
            target_chara_prons_set.add(target_chara_pron)
            target_chara_prons.append(target_chara_pron_split + target_chara_mark)
        else: target_chara_prons.append([])
    return target_chara_prons
    # return 
    
    
# 依照生成音，改韻母聲調，包括 aam 改成 aap、陰入分派上下陰入；在 jgzw 後調用
def adapt_final_versus_tone(target_chara_pron_split: list, target_chara_position:list, tone_config)->list:
    i, f, t = target_chara_pron_split
    c0, c1, c2, c3, c4, c5 = target_chara_position
    long_final_list = ['aam', 'aan', 'im', 'in', 'om', 'on', 'ong', 'oeng', 'un', 'yun']
    short_final_list = ['am', 'an', 'ang', 'eon', 'ing', 'ung']
    if tone_config.有下陰入 and t=='7' and (f not in short_final_list or (f=="am" and c1=="覃")):
        t = '8'
    if tone_config.有下陽入 and t=='9' and (f not in short_final_list or (f=="am" and c1=="覃")):
        t = '10'
    # 給送氣分調留一個位置
    if t in ['7', '8', '9', '10'] and len(f)>1:
        if f[-2:]=='ng': f = f[:-2]+"k"
        elif f[-1]=='n': f = f[:-1]+"t"
        elif f[-1]=='m': f = f[:-1]+"p"
    return [i, f, tone_config.應用調號[t]]
    
    
# 指派調號；在 jgzw 時調用
def retrive_tone_by_position(position_info: list, tone_config):
    result = ""
    c0, c1, c2, c3, c4, c5 = position_info
    jam = c0 not in tone_config.全濁聲紐 and c0 not in tone_config.次濁聲紐
    if c5=="平": result = "1" if jam else "4"
    elif c5=="上": result = "2" if jam else "5"
    elif c5=="去": result = "3" if jam else "6"
    elif c5=="入": result = "7" if jam else "9"
    return result
    

# 濁上歸去，規則在調用程序時使用參數指定；在 jgzw 前調用
def change_tone_class(position_info: list, tone_config):
    c0, c1, c2, c3, c4, c5 = position_info
    if (tone_config.全濁上變去) and (c0 in tone_config.全濁聲紐) and (c5=="上"):
        c5 = "去"
    if tone_config.次濁上變去 and (c0 in tone_config.次濁聲紐) and (c5=="上"):
        c5 = "去"
    return [c0, c1, c2, c3, c4, c5]
    
    
# 依照音韻地位，取得聲母
def retrive_initial_by_position(position_info: list, initial_config):
    v0, v1, v2, v3, v4, v5 = ["_"] * 6 # 匹配項的鍵名（在聲母表）
    c0, c5, c1, c2, c4, c3 = position_info
    # 爲方便，這裏直接加埋非組處理
    if c0 in ["幫","滂","並","明"] and c1=="合" and c2=="三": c0 = "非敷奉微"["幫滂並明".find(c0)]
    for i in initial_config.keys():
        if c0!="" and c0 in i: v0 = i; break
    if v0 not in initial_config: return [""]
    for i in initial_config[v0].keys():
        if c1!="" and c1 in i: v1 = i; break
    if v1 not in initial_config[v0]: return [""]
    for i in initial_config[v0][v1].keys():
        if c2!="" and c2 in i: v2 = i; break
    if v2 not in initial_config[v0][v1]: return [""]
    for i in initial_config[v0][v1][v2].keys():
        if c3!="" and c3 in i: v3 = i; break
    if v3 not in initial_config[v0][v1][v2]: return [""]
    for i in initial_config[v0][v1][v2][v3].keys():
        if c4!="" and c4 in i: v4 = i; break
    if v4 not in initial_config[v0][v1][v2][v3]: return [""]
    for i in initial_config[v0][v1][v2][v3][v4].keys():
        if c5!="" and c5 in i: v5 = i; break
    if v5 not in initial_config[v0][v1][v2][v3][v4]: return [""]
    return initial_config[v0][v1][v2][v3][v4][v5]
    # return ['b', '', '', ''] # 後面三项是特殊字列表
    
    
# 依照音韻地位，取得韻母
def retrive_final_by_position(position_info: list, final_config):
    v0, v1, v2, v3, v4 = ["_"] * 5 # 匹配項的鍵名（在韻母表）
    c4, c3, c1, c2, c0, _ = position_info
    for i in final_config.keys():
        if c0!="" and c0 in i: v0 = i; break
    if v0 not in final_config: return [""]
    for i in final_config[v0].keys():
        if c1!="" and c1 in i: v1 = i; break
    if v1 not in final_config[v0]: return [""]
    for i in final_config[v0][v1].keys():
        if c2!="" and c2 in i: v2 = i; break
    if v2 not in final_config[v0][v1]: return [""]
    for i in final_config[v0][v1][v2].keys():
        if c3!="" and c3 in i: v3 = i; break
    if v3 not in final_config[v0][v1][v2]: return [""]
    for i in final_config[v0][v1][v2][v3].keys():
        if c4!="" and c4 in i: v4 = i; break
    if v4 not in final_config[v0][v1][v2][v3]: return [""]
    return final_config[v0][v1][v2][v3][v4]
    # return ['ung', '', '', ''] # 後面三项是特殊字列表


# 將聲母簡寫擴展爲全寫, eg.「端組來」->「端透定泥來」 # 次濁有調整
def expend_intial_expr(in_abbr: str) -> str:
    result = in_abbr
    result_grp = ""
    result_srs = ""
    if "系" in result: # 「幫見系」 -> 「幫系見系」
        result_srs = result.split("系")
        result = result_srs[1]
        result_srs = "".join([i + "系" for i in result_srs[0]])
    if "組" in result: # 「端精組」 -> 「端組精組」
        result_grp = result.split("組")
        result = result_grp[1]
        result_grp = "".join([i + "組" for i in result_grp[0]])
    result = result_srs + result_grp + result
    result = result.replace("銳音", "端系知系日")
    result = result.replace("鈍音", "幫系見系")
    
    result = result.replace("幫系", "幫組")
    result = result.replace("端系", "端組精組來")
    result = result.replace("知系", "知組莊組章組")
    result = result.replace("見系", "見組影組")
    
    result = result.replace("幫組", "幫滂並明")
    #result = result.replace("非組", "非敷奉微")
    result = result.replace("端組", "端透定泥")
    result = result.replace("精組", "精清從心邪")
    result = result.replace("知組", "知徹澄娘")
    result = result.replace("莊組", "莊初崇生") 
    result = result.replace("章組", "章昌常書船")
    result = result.replace("見組", "見溪群疑")
    result = result.replace("影組", "云影曉匣")
    
    result = result.replace("谿", "溪") # 統一
    result = result.replace("羣", "群")
    result = result.replace("孃", "娘")
    return result
