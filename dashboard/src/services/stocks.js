import axios from "axios";

const API_ROOT = "http://127.0.0.1:8000";

export const getStocks = () => {
  return axios.get(`${API_ROOT}/stock-list`).then((res) => res.data);
};

export const addStock = (stock) => {
  return axios
    .post(`${API_ROOT}/add-stock?stock=${stock}`)
    .then((res) => res.data);
};

export const removeStock = (stock) => {
  return axios
    .post(`${API_ROOT}/remove-stock?stock=${stock}`)
    .then((res) => res.data);
};
