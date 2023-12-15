import { Box, Typography, useTheme } from "@mui/material";
import { tokens } from "../theme";

const StockBox = ({ stockSymbol, shares, price }) => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);

  return (
    <Box width="100%" m="0 20px">
      <Box display="flex" justifyContent="space-between">
        <Box>
          <Typography
            variant="h4"
            fontWeight="bold"
            sx={{ color: colors.grey[100] }}
          >
            {stockSymbol}
          </Typography>
        </Box>

        <Box width="30%" height="30%">
          <img
            alt="profile-user"
            width="100%"
            object-fit="cover"
            src={`../../assets/${stockSymbol}.png`}
            style={{ cursor: "pointer", borderRadius: "10%" }}
          />
        </Box>
      </Box>
      <Box display="flex" justifyContent="space-between" mt="2px">
        <Typography variant="h5" sx={{ color: colors.greenAccent[500] }}>
          {`Shares: ${shares}`}
        </Typography>
        <Typography
          variant="h5"
          fontStyle="italic"
          sx={{ color: colors.greenAccent[600] }}
        >
          ${price}
        </Typography>
      </Box>
    </Box>
  );
};

export default StockBox;
