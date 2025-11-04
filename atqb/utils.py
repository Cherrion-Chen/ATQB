from .student import Stud, StudFrame, avoid_repeat
import pandas as pd
import numpy as np
import types

def from_df(df: pd.DataFrame)->StudFrame:
    op = StudFrame()
    op.from_df(df)
    return op
        
def from_excel(path: str)->StudFrame:
    op = StudFrame()
    op.from_excel(path)
    return op

def sort(sts: StudFrame, column=None, func=None, order='up'):
    '''
    Sort the StudFrame.
    
    Input:
        sts: origin StudFrame
        column: name of information
        func: preprocess function (if there is, it should be like f(x))
        order: up or down
    Output: StudFrame object
    '''
    
    if column is None:
        col = sts.id_list()
    else:
        col = sts.info.index(column)
        col = [sts[r][col+1] for r in range(len(sts))]
    
    if callable(func):
        col = list(map(func, col))
        
    seq = np.argsort(col)
    if order != 'up': seq=seq[::-1]
    return sts[list(seq)]


def cat(*frames: StudFrame):
    '''
    Concatenate all frame you input.
    
    Input: any number of StudFrame objects
    Output: StudFrame object
    '''
    
    name_included = False
    info = ['姓名']

    ids = []
    for frame in frames:
        ids = ids + frame.id_list()
    ids = list(dict.fromkeys(ids))
    studs = [[id, pd.NA] for id in ids]

    for frame in frames:
        fr = frame.copy()
        if '姓名' in fr.info:
            name_included = True
            fr.remove_info('姓名')

        info = info + fr.info
        dct = dict(zip(fr.id_list(), range(len(fr))))

        for r in range(len(studs)):
            id = studs[r][0]
            try:
                ind = dct[id]
                studs[r] = studs[r] + [v for v in fr.studs[ind][1:]]
            except:
                studs[r] = studs[r] + [pd.NA for v in fr.studs[0][1:]]
                continue
                
            try:
                col = frame.info.index('姓名')+1
                studs[r][1] = frame.studs[ind][col]
            except:
                continue
        
    op = StudFrame()
    op.aug = frames[0].aug
    op.info = avoid_repeat(info)
    op.studs = studs
        
    if not name_included:
        op.remove_info('姓名')
    
    return op

def divide_id(id)->dict:
    if isinstance(id, Stud):
        id = id.id

    id = str(id)
    
    try: num = id[-2:]
    except: gra = pd.NA
    
    try: cla = id[-4: -2]
    except: gra = pd.NA
    
    try: gra = id[-8: -4]
    except: gra = pd.NA
    
    return {'gra': gra,
            'cla': cla,
            'num': num}

def get_sum(stus: StudFrame, info_name, func=float, mode='cla')->dict:
    '''
    Sum up specified information of a class or grade.
    '''
    
    op = {}
    ind = stus.info.index(info_name)+1

    for row in stus.studs:
        belong = divide_id(row[0])[mode]

        try: op[belong] += func(row[ind])
        except: op[belong] = func(row[ind])

    return op

def count(stus: StudFrame, judge, mode='cla')->dict:
    '''
    Count the students making judge function return True.
    '''
    
    op = {}
    
    for stu in stus:
        belong = divide_id(stu.id)[mode]

        add = bool(judge(stu))

        try: op[belong] += int(add)
        except: op[belong] = int(add)

    return op

def filter(stus: StudFrame, judge)->StudFrame:
    '''
    Return a StudFrame containing only students making judge return True.
    '''
    
    ls = [i for i in range(len(stus)) if judge(stus[i])]
    return stus[ls]

def filter_cla(stus: StudFrame, cla: str)->StudFrame:
    '''
    Select the students from specified class.
    '''
    
    cla = str(cla)
    cla = '0'*(2-len(cla)) + cla

    ls = [i for i in range(len(stus)) if divide_id(stus.studs[i][0])['cla']==cla]
    return stus[ls]

def filter_gra(stus: StudFrame, gra: str)->StudFrame:
    '''
    Select the students from specified grade.
    '''
    
    gra = str(gra)
    ls = [i for i in range(len(stus)) if divide_id(stus.studs[i][0])['gra']==gra]
    return stus[ls]

def accelerate(sts: StudFrame):
    sts._dct = dict(zip(sts.id_list(), range(len(sts))))

    def _quick_find(self, id):
        if isinstance(id, list):
            return self[[self._dct[i] for i in id]]
        return self[self._dct[id]]
    
    def _quick_set(self, id: str, info_name, value):
        ind = self._dct[id]
        if info_name is None or info_name=='学号':
            col = 0
        else: col = self.info.index(info_name)+1
        
        self.studs[ind][col] = value
    
    sts.quick_find = types.MethodType(_quick_find, sts)
    sts.quick_set = types.MethodType(_quick_set, sts)
