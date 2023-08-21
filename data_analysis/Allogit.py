import pandas as pd
import numpy as np
import os
import sys
import statsmodels.api as sm
import statsmodels.formula.api as sf 

def __lgt__(endog,exog):
    temp=endog.mean()
    endog=endog.apply(lambda x:1 if x > endog.mean() else 0)
    process=sm.Logit(endog=endog,exog=sm.add_constant(exog)).fit()
    p_test=process.pvalues.sort_values(ascending=False).to_frame()
    i=0
    while any(p_test[0]>0.05):
        exog=exog[exog.columns.difference([p_test.index[0]])]
        process=sm.Logit(endog=endog,exog=sm.add_constant(exog)).fit()
        p_test=process.pvalues.sort_values(ascending=False).to_frame()
        i+=1
        if i>4:
            break
    return [process,temp]

col_base=["삶의 사다리 점수",'(가)건강 만족도','(나)가족의 수입 만족도','(다)주거 환경 만족도','(라)가족관계 만족도','(마)직업 만족도','(바)사회적 친분관계 만족도','(사)여가생활 만족도']

def Lgt(data,col_name=None):
    if col_name:
        result={}
        for val in data[col_name].unique():
            use_data=data[data[col_name]==val][col_base]
            sub_data={"중상위":use_data,"최상위":use_data[use_data["삶의 사다리 점수"]>use_data["삶의 사다리 점수"].mean()]
                      ,"최하위":use_data[use_data["삶의 사다리 점수"]<=use_data["삶의 사다리 점수"].mean()]}
            sub_result={}
            for key in sub_data:
                endog=sub_data[key]["삶의 사다리 점수"]
                exog=sub_data[key][col_base[1:]]
                sub_result[key]=__lgt__(endog,exog)
            result[val]=sub_result
        return result
    else:
        use_data=data[col_base]
        sub_data={"중상위":use_data,"최상위":use_data[use_data["삶의 사다리 점수"]>use_data["삶의 사다리 점수"].mean()]
                      ,"최하위":use_data[use_data["삶의 사다리 점수"]<=use_data["삶의 사다리 점수"].mean()]}
        sub_result={}
        for key in sub_data:
            endog=sub_data[key]["삶의 사다리 점수"]
            exog=sub_data[key][col_base[1:]]
            sub_result[key]=__lgt__(endog,exog)
        return sub_result