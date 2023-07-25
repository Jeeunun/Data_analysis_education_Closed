import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
import statsmodels.stats.anova as anova
import bs4
import statsmodels.stats.outliers_influence as so
class OLS:
    def __init__(self,formula:str,data) -> None:
        self.__name__="main"
        self.__models__={"not_fit":smf.ols(formula,data),"fit":smf.ols(formula,data).fit()}
        self.__info__=dict.fromkeys(['df_model','df_resid','pvalues',
                                 'f_pvalue','f_test','fvalue','params','resid',
                                 'rsquared','rsquared_adj','tvalues',
                                 'conf_int','aic','bic','bse','cov_kwds'])
        for x in self.__info__:
            self.__info__[x]=eval(f'self.__models__["fit"].{x}')
        # OLS이므로 지금은 이렇게 계산하지만 차후 고쳐야함.
        for i in range(len(self.__models__["not_fit"].exog_names)):
            VIF=so.variance_inflation_factor(self.__models__["not_fit"].exog,i)
        self.__info__["VIF"]=VIF
        self.__info__["x_name"]=self.__models__["not_fit"].exog_names[1:]
        self.__info__["y_name"]=self.__models__["not_fit"].endog_names
        pass
    def summary(self,want_table=False):
        if want_table:
            return self.__models__["fit"].summary().tables
        else:
            return self.__models__["fit"].summary()
    def report_main(self,p=0.05):
        temp={
            0.05 : 1,
            0.01 : 2,
            0.001 : 3
        }
        i=self.__info__
        item = {
        "독립변수": i['x_name'],
        "B": i['params'][1:],
        "표준오차": i['bse'][1:],
        # 일단 beta : 0 으로 고정해놨음
        "β": 0,
        "t": list(map(lambda x:str(x)+("*"*temp[p]),i['tvalues']))[1:],
        "유의확률" : i['pvalues'][1:],
        "VIF": i["VIF"]
    }
        report=pd.DataFrame(item)
        report.index=[self.__info__["y_name"]]
        report.index.rename('종속변수',inplace=True)
    def report_sub(self):
        i=self.__info__
        x=pd.read_html(self.__models__["fit"].summary().tables[2].as_html())[0].loc[0][3]
        return f"𝑅:{i['rsquared']}, 𝑅^2:{i['rsquared_adj']}, 𝐹:{i['fvalue']}, 유의확률:{i['f_pvalue']}, Durbin-Watson:{x}"