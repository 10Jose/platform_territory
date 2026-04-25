import { request } from "./apiClient";

export const getRanking = async () => {
    return request("/ranking");
};

export const getIndicators = async () => {
    return request("/indicators");
};