DETAILED POWER BI DASHBOARD PROMPT

ROLE & CONTEXT
You are a senior Power BI developer and data analyst. Your task is to design a professional, executive-ready Power BI dashboard for business decision-making.

OBJECTIVE
Create an interactive Sales Performance Dashboard for a mid-size Indian retail company to help management analyze sales, profitability, customer trends, and regional performance.

DATA DESCRIPTION

Table 1: Sales
- OrderID
- OrderDate
- CustomerID
- ProductID
- Region
- State
- SalesAmount
- Quantity
- Discount
- Profit

Table 2: Customers
- CustomerID
- CustomerName
- CustomerSegment (Consumer / Corporate / Small Business)
- City
- State

Table 3: Products
- ProductID
- ProductName
- Category
- Sub-Category

Table 4: Calendar
- Date
- Year
- Quarter
- Month
- MonthYear

DATA MODELING REQUIREMENTS
- Use a star schema
- Mark Calendar as Date Table
- Relationships:
  Sales.CustomerID → Customers.CustomerID
  Sales.ProductID → Products.ProductID
  Sales.OrderDate → Calendar.Date

KEY DAX MEASURES TO CREATE
- Total Sales
- Total Profit
- Profit Margin %
- Total Quantity Sold
- Average Order Value
- YTD Sales
- YoY Growth %
- Top 5 Products by Sales
- Top 5 Customers by Profit

VISUALS TO INCLUDE

KPI Cards
- Total Sales
- Total Profit
- Profit Margin %
- Year-over-Year Growth %

Charts
- Line Chart: Monthly Sales Trend
- Clustered Column Chart: Sales by Category
- Bar Chart: Top 10 Products by Sales
- Map: Sales by State
- Donut Chart: Sales by Customer Segment

Table Visual
- Product-wise Sales, Quantity, Profit, Margin %

FILTERS / SLICERS
- Year
- Quarter
- Region
- Category
- Customer Segment

DESIGN & UX GUIDELINES
- Professional corporate theme
- Consistent colors for Sales and Profit
- Drill-through from summary to product detail
- Tooltips for Sales, Profit, Margin
- Optimized for performance and readability

INSIGHTS TO HIGHLIGHT
- Best performing region and category
- Loss-making products
- Seasonal sales patterns
- High-value customer segments

FINAL OUTPUT EXPECTATIONS
- Executive-ready Power BI report
- Clean naming for measures and visuals
- Scalable design for future growth
- Short explanation of insights and business recommendations

