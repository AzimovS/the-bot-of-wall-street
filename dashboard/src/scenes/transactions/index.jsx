import { useState, useEffect } from "react";
import { Box } from "@mui/material";
import { DataGrid, GridToolbar } from "@mui/x-data-grid";
import { tokens } from "../../theme";
import { mockTransactions } from "../../data/mockData";
import Header from "../../components/Header";
import { useTheme } from "@mui/material";
import { getTransactions } from "../../services/stocks";

function getRowId(row) {
  return `${row.table}-${row._time}` ;
}

const Transactions = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const [transactions, setTransactions] = useState([]);

  const getTransactionsData = () => {
    getTransactions().then((res) => {
      setTransactions(res);
    });
  };

  useEffect(() => {
    getTransactionsData();
  }, []);

  const columns = [
    { field: "table", headerName: "ID", flex: 0.2 },
    {
      field: "_time",
      headerName: "Time",
      flex: 0.5,
      renderCell: ({ row: { _time } }) => {
        return <Box>{_time?.slice(0, 19)}</Box>;
      },
    },
    { field: "_measurement", headerName: "Stock Symbol", flex: 0.2 },
    {
      field: "price",
      headerName: "Price",
      cellClassName: "name-column--cell",
      flex: 0.2,
      renderCell: ({ row: { price } }) => {
        return <Box>${parseFloat(price).toFixed(3)}</Box>;
      },
    },
    {
      field: "predicted_price",
      headerName: "Predicted Price",
      cellClassName: "name-column--cell",
      flex: 0.2,
      renderCell: ({ row: { predicted_price } }) => {
        return <Box>${parseFloat(predicted_price).toFixed(3)}</Box>;
      },
    },
    {
      field: "action",
      headerName: "Action",
      flex: 0.2,
      renderCell: ({ row: { action } }) => {
        return (
          <Box
            width="40%"
            p="5px"
            display="flex"
            justifyContent="center"
            backgroundColor={
              action === "buy" ? colors.greenAccent[600] : colors.redAccent[600]
            }
            borderRadius="4px"
          >
            {action === "buy" ? "BUY" : "SELL"}
          </Box>
        );
      },
    },
    {
      field: "_value",
      headerName: "Profit",
      flex: 0.2,
      cellClassName: "name-column--cell",
      renderCell: ({ row: { _value } }) => {
        return <Box>${parseFloat(_value).toFixed(3)}</Box>;
      },
    },
  ];

  return (
    <Box m="20px">
      <Header title="TRANSACTIONS" subtitle="List of Transactions" />
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
          "& .MuiDataGrid-toolbarContainer .MuiButton-text": {
            color: `${colors.grey[100]} !important`,
          },
        }}
      >
        <DataGrid
          getRowId={getRowId}
          rows={transactions}
          columns={columns}
          components={{ Toolbar: GridToolbar }}
        />
      </Box>
    </Box>
  );
};

export default Transactions;
