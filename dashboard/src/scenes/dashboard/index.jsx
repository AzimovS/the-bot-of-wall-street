import { useState, useEffect } from "react";
import { Box, Typography, useTheme } from "@mui/material";
import { tokens } from "../../theme";
import { mockTransactions, mockStocks } from "../../data/mockData";
import MonetizationOnIcon from "@mui/icons-material/MonetizationOn";
import Header from "../../components/Header";
import StatBox from "../../components/StatBox";
import StockBox from "../../components/StockBox";
import { getPortfolio, getTransactions } from "../../services/stocks";

const Dashboard = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const [portfolio, setPortfolio] = useState([]);
  const [isLoading, SetIsLoading] = useState(true);
  const [transactions, setTransactions] = useState([]);

  useEffect(() => {
    let interval = setInterval(
      () => {
        SetIsLoading(false);
        getPortfolio().then((res) => {
          setPortfolio(res);
        });
        getTransactions().then((res) => {
          setTransactions(res);
        });
      },
      isLoading ? 1000 : 5000
    );
    return () => {
      clearInterval(interval);
    };
  }, []);

  return (
    <Box m="0 30px 30px 30px">
      {/* HEADER */}
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Header title="DASHBOARD" subtitle="Welcome to your dashboard" />
      </Box>
      {/* GRID & CHARTS */}
      <Box
        display="grid"
        gridTemplateColumns="repeat(12, 1fr)"
        gridAutoRows="140px"
        gap="20px"
      >
        {/* ROW 1 */}
        <Box
          gridColumn="span 2"
          backgroundColor={colors.primary[400]}
          display="flex"
          alignItems="center"
          justifyContent="center"
        >
          <StatBox
            title={portfolio.reduce((accumulator, stock) => {
              return accumulator + stock.shares * stock.price;
            }, 0)}
            subtitle="Current portfolio"
            icon={
              <MonetizationOnIcon
                sx={{ color: colors.greenAccent[600], fontSize: "26px" }}
              />
            }
          />
        </Box>
        {/* <Box
          gridColumn="span 2"
          backgroundColor={colors.primary[400]}
          display="flex"
          alignItems="center"
          justifyContent="center"
        >
          <StatBox
            title="$3225"
            subtitle="Profit"
            icon={
              <ShowChartIcon
                sx={{ color: colors.greenAccent[600], fontSize: "40px" }}
              />
            }
          />
        </Box> */}
        <Box
          gridColumn="span 10"
          display="flex"
          alignItems="center"
          justifyContent="center"
        ></Box>
      </Box>
      <Box
        mt={"20px"}
        display="flex"
        justifyContent="space-between"
        alignItems="center"
      >
        <Typography
          variant="h4"
          color={colors.grey[100]}
          fontWeight="bold"
          sx={{ m: "0 0 5px 0" }}
        >
          Stocks
        </Typography>
      </Box>
      {/* GRID & CHARTS */}
      <Box
        display="grid"
        gridTemplateColumns="repeat(15, 1fr)"
        gridAutoRows="140px"
        gap="20px"
      >
        {/* ROW 2 */}
        {isLoading
          ? "Loading..."
          : portfolio.length === 0
          ? "You don't have any stocks"
          : portfolio.map((stock, index) => (
              <Box
                key={index}
                gridColumn="span 3"
                backgroundColor={colors.primary[400]}
                display="flex"
                alignItems="center"
                justifyContent="center"
              >
                <StockBox
                  stockSymbol={stock.symbol}
                  shares={stock.shares}
                  price={stock.price}
                />
              </Box>
            ))}

        {/* ROW 3 */}
        <Box
          gridColumn="span 15"
          gridRow="span 2"
          backgroundColor={colors.primary[400]}
          overflow="auto"
        >
          <Box
            display="flex"
            justifyContent="space-between"
            alignItems="center"
            borderBottom={`4px solid ${colors.primary[500]}`}
            colors={colors.grey[100]}
            p="15px"
          >
            <Typography color={colors.grey[100]} variant="h5" fontWeight="600">
              Recent Transactions
            </Typography>
          </Box>
          {transactions.map((transaction, i) => (
            <Box
              key={`${transaction.table}-${transaction._time}`}
              display="flex"
              justifyContent="space-between"
              alignItems="center"
              borderBottom={`4px solid ${colors.primary[500]}`}
              p="15px"
            >
              <Box flex="1" minWidth="0">
                <Typography
                  color={colors.greenAccent[500]}
                  variant="h5"
                  fontWeight="600"
                >
                  {transaction._measurement}
                </Typography>
              </Box>

              <Box flex="1" color={colors.grey[100]}>
                {transaction._time?.slice(0, 19)}
              </Box>
              <Box flex="1" color={colors.grey[100]}>
                {transaction?.action === "buy" ? "BUY" : "SELL"}
              </Box>
              <Box flex="1" color={colors.grey[100]}>
                ${parseFloat(transaction?.price).toFixed(3)}
              </Box>
            </Box>
          ))}
        </Box>
      </Box>
    </Box>
  );
};

export default Dashboard;
