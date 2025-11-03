from atqb import *

students = pd.DataFrame(pd.read_excel(input('请拖入学生信息：')))
weights = pd.DataFrame(pd.read_excel(input('请拖入权重文件：')))
weights.set_index('教材', inplace=True)

def weighted_sum(s: Stud, weights):
    sum = 0
    for i in s.info:
        try:
            sum += float(weights.loc[s[i]]['价格'])
        except: ...
    return sum

ls = from_df(students)
op = ls.map(weighted_sum, other_args=weights, info_name='总价')
print(op)
op.to_excel()
