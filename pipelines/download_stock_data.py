import yfinance as yf

sp500 = "MMM AOS ABT ABBV ABMD ACN ATVI ADBE AAP AMD AES AFL A APD AKAM ALK ALB ARE ALXN ALGN ALLE LNT ALL GOOGL GOOG MO AMZN AMCR AEE AAL AEP AXP AIG AMT AWK AMP ABC AME AMGN APH ADI ANSS ANTM AON APA AAPL AMAT APTV ADM ANET AJG AIZ T ATO ADSK ADP AZO AVB AVY BKR BLL BAC BAX BDX BRK.B BBY BIO BIIB BLK BA BKNG BWA BXP BSX BMY AVGO BR BF.B CHRW COG CDNS CPB COF CAH KMX CCL CARR CTLT CAT CBOE CBRE CDW CE CNC CNP CERN CF SCHW CHTR CVX CMG CB CHD CI CINF CTAS CSCO C CFG CTXS CME CMS KO CTSH CL CMCSA CMA CAG COP ED STZ CPRT GLW CTVA COST CCI CSX CMI CVS DHI DHR DRI DVA DE DAL XRAY DVN DXCM FANG DLR DFS DISCA DISCK DISH DG DLTR D DPZ DOV DOW DTE DUK DRE DD DXC EMN ETN EBAY ECL EIX EW EA EMR ENPH ETR EOG EFX EQIX EQR ESS EL ETSY RE EVRG ES EXC EXPE EXPD EXR XOM FFIV FB FAST FRT FDX FIS FITB FRC FE FISV FLT FLIR FLS FMC F FTNT FTV FBHS FOXA FOX BEN FCX GPS GRMN IT GD GE GIS GM GPC GILD GPN GL GS GWW HAL HBI HIG HAS HCA PEAK HSIC HES HPE HLT HFC HOLX HD HON HRL HST HWM HPQ HUM HBAN HII IEX IDXX INFO ITW ILMN INCY IR INTC ICE IBM IFF IP IPG INTU ISRG IVZ IPGP IQV IRM JBHT JKHY J SJM JNJ JCI JPM JNPR KSU K KEY KEYS KMB KIM KMI KLAC KHC KR LB LHX LH LRCX LW LVS LEG LDOS LEN LLY LNC LIN LYV LKQ LMT L LOW LUMN LYB MTB MRO MPC MKTX MAR MMC MLM MAS MA MXIM MKC MCD MCK MDT MRK MET MTD MGM MCHP MU MSFT MAA MHK TAP MDLZ MPWR MNST MCO MS MSI MSCI NDAQ NTAP NFLX NWL NEM NWSA NWS NEE NLSN NKE NI NSC NTRS NOC NLOK NCLH NOV NRG NUE NVDA NVR ORLY OXY ODFL OMC OKE ORCL OTIS PCAR PKG PH PAYX PAYC PYPL PNR PBCT PEP PKI PRGO PFE PM PSX PNW PXD PNC POOL PPG PPL PFG PG PGR PLD PRU PEG PSA PHM PVH QRVO QCOM PWR DGX RL RJF RTX O REG REGN RF RSG RMD RHI ROK ROL ROP ROST RCL SPGI CRM SBAC SLB STX SEE SRE NOW SHW SPG SWKS SLG SNA SO LUV SWK SBUX STT STE SYK SIVB SYF SNPS SYY TMUS TROW TTWO TPR TGT TEL TDY TFX TER TSLA TXN TXT BK CLX COO HSY MOS TRV DIS TMO TJX TSCO TT TDG TRMB TFC TWTR TYL TSN USB UDR ULTA UAA UA UNP UAL UPS URI UNH UHS UNM VLO VAR VTR VRSN VRSK VZ VRTX VFC VIAC VTRS V VNT VNO VMC WRB WBA WMT WM WAT WEC WFC WELL WST WDC WU WAB WRK WY WHR WMB WLTW WYNN XEL XRX XLNX XYL YUM ZBRA ZBH ZION ZTS"

def main():
    for symbol in sp500.split(' '):
        data = yf.download(symbol, start="1987-01-01", end="2017-12-31")
        data.to_csv(f'../raw/{symbol}.csv')

if __name__ == '__main__':
    main()