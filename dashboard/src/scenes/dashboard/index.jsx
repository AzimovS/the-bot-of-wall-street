import { Box, Typography, Stack, useTheme } from "@mui/material";
import { tokens } from "../../theme";
import { mockTransactions, mockStocks } from "../../data/mockData";
import MonetizationOnIcon from "@mui/icons-material/MonetizationOn";
import ShowChartIcon from "@mui/icons-material/ShowChart";
import EmailIcon from "@mui/icons-material/Email";
import PointOfSaleIcon from "@mui/icons-material/PointOfSale";
import PersonAddIcon from "@mui/icons-material/PersonAdd";
import TrafficIcon from "@mui/icons-material/Traffic";
import Header from "../../components/Header";
import StatBox from "../../components/StatBox";
import StockBox from "../../components/StockBox";

const Dashboard = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);

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
            title="$12361"
            subtitle="Current portfolio"
            icon={
              <MonetizationOnIcon
                sx={{ color: colors.greenAccent[600], fontSize: "26px" }}
              />
            }
          />
        </Box>
        <Box
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
        </Box>
        <Box
          gridColumn="span 8"
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
        {mockStocks.map((stock, i) => (
          <Box
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
          {mockTransactions.map((transaction, i) => (
            <Box
              key={`${transaction.txId}-${i}`}
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
                  {transaction.symbol}
                </Typography>
                <Typography color={colors.grey[100]}>
                  {transaction.txId}
                </Typography>
              </Box>

              <Box flex="1" color={colors.grey[100]}>
                {transaction.time}
              </Box>
              <Box flex="1" color={colors.grey[100]}>
                {transaction.action}
              </Box>
              <Box flex="1" color={colors.grey[100]}>
                {transaction.cost}
              </Box>
              <Box flex="1" color={colors.grey[100]}>
                {transaction.profit}
              </Box>

              <Box
                backgroundColor={colors.greenAccent[500]}
                p="5px 10px"
                borderRadius="4px"
              >
                ${transaction.cost}
              </Box>
            </Box>
          ))}
        </Box>
      </Box>
    </Box>
  );
};

export default Dashboard;
