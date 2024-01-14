import { Box } from "@mui/material";
import Header from "../../components/Header";
import PortfolioPieChart from "../../components/PortfolioPieChart";

const PortfolioChart = () => {
  return (
    <Box m="20px">
      <Header title="Pie Chart" subtitle="Simple Pie Chart" />
      <Box height="75vh">
        <PortfolioPieChart />
      </Box>
    </Box>
  );
};

export default PortfolioChart;
