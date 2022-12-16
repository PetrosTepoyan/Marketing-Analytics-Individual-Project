import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import squarify

class RFMAnalysis:
    """
    An instance of this class can be used to perform RFM analysis, with different output types, 
    such as tables and plots.
    
    Attributes
    ----------
    data_path : str
        path to the dataframe
    customer : str
        column name for `customer` data
    revenue : str
        column name for `revenue` data
    date : str
        column name for `date` data
        
    Methods
    -------
    problemsolver(self)
    
    best_customers(self, n, n_quantiles = 4)
        
    worst_customers(self, n, n_quantiles = 4)
    
    table(self, n_quantiles = 4)
    
    table_grouped(self, n_quantiles = 4)
    
    plot_revenue(self)
    
    plot_segments(self, n_quantiles = 4)
    
    plot_traits(self, n_quantiles = 4)
    
    plot_segments_lines(self, n_quantiles = 4)
    """
    
    def __init__(self, data_path, customer, date, revenue):
        """
        Initializes the object.
        
        Parameters
        ----------
        data_path : str
            Path to the CSV file
        customer : str
            name of the event column 
        date : str
            name of the time column 
        revenue : str
            name of the group_by column 
        """
        
        try:
            self.data = pd.read_csv(data_path, parse_dates = [date])
        except FileNotFoundError:
            print("Error | Could not find the CSV file. Please, check that the requested file exists and is located in the working directory")
            return
        except ValueError:
            print("Error | Could not locate `date` column to parse dates")
            return 
        
        self.customer = customer
        self.date = date
        self.revenue = revenue
        
        if customer not in self.data:
            print("Error | Could not locate `customer` column. Please, check input.")
            
        if date not in self.data:
            print("Error | Could not locate `date` column. Please, check input.")
        
        if revenue not in self.data:
            print("Error | Could not locate `revenue` column. Please, check input.")
            
    def problemsolver(self):
        """
        Plots all available charts
        """
        self.plot_revenue()
        self.plot_segments()
        self.plot_traits()
        self.plot_segments_lines()
        
        best_3 = list(self.best_customers(3)[self.customer])
        worst_3 = list(self.worst_customers(3)[self.customer])
        print("Best:", ", ".join(best_3))
        print("Worst:", ", ".join(worst_3))
    
    def best_customers(self, n, n_quantiles = 4):
        """
        Outputs the best `n` customers. 
        
        Parameters
        ----------
        n : int
            Number of the best customers to return.
        n_quantiles: int
            Number of quantiles to use during analysis.
        """
        
        rfm = self.table(n_quantiles)
        
        if rfm is None:
            return
        
        best = rfm.head(n)
            
        return best[[self.customer, "RFM_Score"]]
    
    def worst_customers(self, n, n_quantiles = 4):
        """
        Outputs the worst `n` customers. 
        
        Parameters
        ----------
        n : int
            Number of the worst customers to return.
        n_quantiles: int
            Number of quantiles to use during analysis.
        """
        
        rfm = self.table(n_quantiles)
        
        if rfm is None:
            return
        
        best = rfm.tail(n)
            
        return best[[self.customer, "RFM_Score"]]
        
    def table(self, n_quantiles = 4):
        """
        Returns an aggregate table with Recency, Frequency and Monetary columns. In addition, 
        it outputs scores in the same table for each customer.
        
        Parameters
        ----------
        n_quantiles: int
            Number of quantiles to use during analysis.
        """
        
        max_date = self.data[self.date].max()
        agg_dict = {'order_date': lambda date: (max_date - date.max()).days,
                    'customer_id': lambda num: len(num), 
                    'revenue': lambda price: price.sum()}
        rfm = self.data.groupby(self.customer).agg(agg_dict) 
        rfm.columns = ['Recency', 'Frequency', 'Monetary']
        rfm.reset_index(inplace = True) 
        
        quantiles = [str(q) for q in range(1, n_quantiles + 1)]
        
        try:
            rfm['R'] = pd.qcut(rfm['Recency'], n_quantiles, quantiles)
            rfm['F'] = pd.qcut(rfm['Frequency'], n_quantiles, quantiles[::-1])
            rfm['M'] = pd.qcut(rfm['Monetary'], n_quantiles, quantiles[::-1])
        except ValueError:
            print("Error | too many quantiles provided. Try a smaller value.")
            return None
        
        rfm['RFM_Score'] = rfm.R.astype(int) + rfm.F.astype(int) + rfm.M.astype(int)
        rfm['RFM_Segment'] = rfm.R.astype(str) + rfm.F.astype(str) + rfm.M.astype(str)
        
        rfm = rfm.sort_values('RFM_Segment', ascending = False)
        
        rfm['Segment_Name'] = rfm.apply(self.__naming, axis=1)
        
        return rfm
    
    def table_grouped(self, n_quantiles = 4):
        """
        Returns an a grouped table with Recency, Frequency and Monetary columns with mean
        function applied to each.
        
        Parameters
        ----------
        n_quantiles: int
            Number of quantiles to use during analysis.
        """
        
        rfm = self.table(n_quantiles)
        
        if rfm is None:
            return
        
        agg_dict = {'Recency': 'mean',
                    'Frequency': 'mean',
                    'Monetary': ['mean', 'count']
                   }

        grouped_by = rfm.groupby('Segment_Name').agg(agg_dict).round(1)
        grouped_by.columns = ['RecencyMean','FrequencyMean','MonetaryMean', 'Count']
        return grouped_by
    
    def plot_revenue(self):
        """
        Plot the revenue.
        """
        
        self.data[self.revenue].hist()
        plt.title('Histogram of Revenue')
        plt.show()
        
    def plot_segments(self, n_quantiles = 4):
        """
        Plot segments.
        
        Parameters
        ----------
        n_quantiles: int
            Number of quantiles to use during analysis.
        """
        
        rfm_grouped = self.table_grouped(n_quantiles)
        
        if rfm is None:
            return
        
        fig = plt.gcf()
        ax = fig.add_subplot()
        
        squarify.plot(sizes = rfm_grouped['Count'], label = RFMAnalysis.__default_score_codes, alpha = .6 )
        plt.title("RFM Segments", fontsize = 18, fontweight = "bold") 
        plt.axis('off')
        plt.show()
    
    def plot_traits(self, n_quantiles = 4):
        """
        Plot density charts for Recency, Frequency, Monetary.
        
        Parameters
        ----------
        n_quantiles: int
            Number of quantiles to use during analysis.
        """
        
        rfm = self.table(n_quantiles)
        
        if rfm is None:
            return
        
        fig, ax = plt.subplots(nrows = 3, ncols = 1, figsize = (10,10))
        sns.distplot(rfm['Recency'], ax = ax[0])
        sns.distplot(rfm['Frequency'], ax = ax[1]) 
        sns.distplot(rfm['Monetary'], ax = ax[2])
        plt.show()
            
    def plot_segments_lines(self, n_quantiles = 4):
        """
        Plot lines for each segment. 
        
        Parameters
        ----------
        n_quantiles: int
            Number of quantiles to use during analysis.
        """
        
        rfm = self.table(n_quantiles)
        
        if rfm is None:
            return
        
        rfm_segments = rfm.groupby('RFM_Segment').count().reset_index(level = 0)
        rfm_segments.plot.barh(x = 'RFM_Segment', y = self.customer)
        plt.show()
        
    def __naming(self, df):
        
        if df['RFM_Score'] >= 9:
            return 'Can\'t Loose Them'
        elif ((df['RFM_Score'] >= 8) and (df['RFM_Score'] < 9)):
            return 'Champions'
        elif ((df['RFM_Score'] >= 7) and (df['RFM_Score'] < 8)):
            return 'Loyal/Commited'
        elif ((df['RFM_Score'] >= 6) and (df['RFM_Score'] < 7)):
            return 'Potential'
        elif ((df['RFM_Score'] >= 5) and (df['RFM_Score'] < 6)):
            return 'Promising'
        elif ((df['RFM_Score'] >= 4) and (df['RFM_Score'] < 5)):
            return 'Requires Attention'
        else:
            return 'Demands Activation'
        
        
    __default_score_codes = ["Can't lose\nthem",
                             "Chapmions",
                             "Loyal/\nCommitted",
                             "Potential",
                             "Promising", 
                             "Requires\nAttention", 
                             "Demans\nActivation"]