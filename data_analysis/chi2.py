import pandas as pd
import scipy.stats as sps
import itertools as it
def chi2_try(data,prt=True):
    #모든 행들의 pair 만들기
    cols=[list(col) for col in it.combinations(data.columns,r=2)]
    result={"Pass":[],
            "type1":[],
            'type2':[],
            'type3':[],
            "type4":[]}
    #전역 탐색
    for col in cols:
        #crosstab 만들기
        step1=pd.crosstab(data[col[0]],data[col[1]],margins=True)
        step2=pd.crosstab(data[col[0]],data[col[1]])
        #chi2 검사 #자유도가 1일떄 좀더 느슨한 검정을 위해 correction=False
        k2=sps.chi2_contingency(step2,correction=False)
        df=pd.DataFrame(k2[3])
        df.index.name=step2.index.name
        df.index=step2.index
        df.columns.name=step2.columns.name
        df.columns=step2.columns
        step3={"Pairs":col,'DataFrame':df,"pvalue":k2[1],"dof":k2[2]}
        itOkay=True
        #전체 관측수가 30보다 작으면 안됨 : type1 error
        if step1.loc["All","All"]<30:
            result["type1"].append(step3)
            itOkay=False
        else:
            #자유도가 1인 경우 모든 기대도수가 5를 넘겨야함 : type2 error
            if k2[2]==1:
                if df[df>5].isna().sum().sum():
                    result["type2"].append(step3)
                    itOkay=False
            #자유도가 1보다 크면 5보다 기대도수의 갯수가 전체의 20%를 넘기면 안됨 : type3 error
            else:
                if df[df>5].isna().sum().sum()>len(step2.columns)*len(step2.index)*0.2:
                    result["type3"].append(step3)
                    itOkay=False
                #위의 조건을 만족하여도 모든 셀의 기대도수가 1을 넘겨야함
                else:
                    if df[df>=1].isna().sum().sum():
                        result["type4"].append(step3)
                        itOkay=False
        #모든 검사 결과 괜찮다면
        if itOkay:
            result["Pass"].append(step3)
    return result