import { useState, useEffect } from "react";
import { Box, IconButton, useTheme } from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { tokens } from "../../theme";
import PlayCircleFilledWhiteIcon from "@mui/icons-material/PlayCircleFilledWhite";
import StopCircleIcon from "@mui/icons-material/StopCircle";
import Header from "../../components/Header";
import { addStock, getStocks, removeStock } from "../../services/stocks";

function getRowId(row) {
  return row.symbol;
}

const Stocks = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const [stocks, setStocks] = useState([]);

  const getStocksData = () => {
    getStocks().then((res) => {
      setStocks(res);
    });
  };

  useEffect(() => {
    getStocksData();
  }, []);

  const startTracking = (stock) => {
    addStock(stock)
      .then((res) => {
        toast.success(`${res?.message} 🫡`);
        getStocksData();
      })
      .catch((err) => {
        toast.error(`${err?.response?.data?.detail} 😡`);
      });
  };

  const stopTracking = (stock) => {
    removeStock(stock)
      .then((res) => {
        toast.success(`${res?.message} 🥲`);
        getStocksData();
      })
      .catch((err) => {
        toast.error(`${err?.response?.data?.detail} 😡`);
      });
  };

  const columns = [
    { field: "symbol", headerName: "Symbol" },
    {
      field: "securityName",
      headerName: "Security Name",
      flex: 2,
      cellClassName: "name-column--cell",
    },
    {
      field: "listingExchange",
      headerName: "Listing Exchange",
      flex: 1,
      cellClassName: "name-column--cell",
    },
    {
      field: "marketCategory",
      headerName: "Market Category",
      flex: 1,
    },
    {
      field: "_value",
      headerName: "Tracking",
      renderCell: ({ row: { symbol, _value: tracking } }) => {
        return (
          <Box>
            {!tracking ? (
              <IconButton
                size="large"
                color="success"
                onClick={() => startTracking(symbol)}
              >
                <PlayCircleFilledWhiteIcon />
              </IconButton>
            ) : (
              <IconButton
                size="large"
                color="warning"
                onClick={() => stopTracking(symbol)}
              >
                <StopCircleIcon />
              </IconButton>
            )}
          </Box>
        );
      },
    },
  ];

  return (
    <Box m="20px">
      <Header title="STOCKS" subtitle="Managing the portfolio" />
      <Box
        m="40px 0 0 0"
        height="75vh"
        sx={{
          "& .MuiDataGrid-root": {
            border: "none",
          },
          "& .MuiDataGrid-cell": {
            borderBottom: "none",
          },
          "& .name-column--cell": {
            color: colors.greenAccent[300],
          },
          "& .MuiDataGrid-columnHeaders": {
            backgroundColor: colors.blueAccent[700],
            borderBottom: "none",
          },
          "& .MuiDataGrid-virtualScroller": {
            backgroundColor: colors.primary[400],
          },
          "& .MuiDataGrid-footerContainer": {
            borderTop: "none",
            backgroundColor: colors.blueAccent[700],
          },
          "& .MuiCheckbox-root": {
            color: `${colors.greenAccent[200]} !important`,
          },
        }}
      >
        <DataGrid getRowId={getRowId} rows={stocks} columns={columns} />
      </Box>
    </Box>
  );
};

export default Stocks;
