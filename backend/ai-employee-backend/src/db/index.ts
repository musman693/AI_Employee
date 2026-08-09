import { pool } from "../config/db";

export const query = (text: string, params?: any[]) => pool.query(text, params);
