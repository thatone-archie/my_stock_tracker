This is the prompt used to generate this file:


Act as an expert Python and web developer. I want to build a simple, clean stock tracking website that mimics the look of modern trading platforms. 
Please write the complete code and setup steps based on these strict requirements:
1. TECH STACK: Use Python with Streamlit for the web framework. Use the 'yfinance' library to fetch all financial data. Use Plotly or Streamlit's native line charts for the graphs.
2. TICKERS TO TRACK: Create a grid layout to show charts for exactly these 10 tickers:
   - TSLA (Tesla)
   - META (Meta)
   - MU (Micron)
   - WDC (Western Digital)
   - NVMI (Nova)
   - MRVL (Marvell Tech)
   - SOXX (iShares Semiconductor ETF)
   - SPY (SPDR S&P 500 ETF)
   - IAU (iShares Gold Trust)
   - RKLB (Rocket Lab Corp)
3. CHART REQUIREMENTS:
   - Each stock must have a time-frame selector to toggle between a 1-Day (1D) and 5-Day (5D) line graph.
   - Do NOT auto-refresh the data. Add a clear "Refresh Data" button at the top of the website so users can update the data manually.
4. METRICS & DATA:
   - Directly underneath each chart, display the stock's Daily Volume.
   - Also display the Next Earnings Date for that specific ticker. If an ETF (like SPY or SOXX) or asset doesn't have an earnings date, display "N/A" or "Not Applicable" gracefully.
5. LOOK AND FEEL: Keep the design clean, organized, and professional, similar to a standard stock trading platform dashboard (using a grid of cards for the 10 tickers).
6. ERROR HANDLING: If the yfinance API fails to load data for a specific ticker, catch the error and display a friendly, clean message to the user instead of breaking the page.
Provide the complete code in a single file if possible, and include short, clear steps on how to install the required libraries and run the app locally.
Ask me any questions if you have any doubts
