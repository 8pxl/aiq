import { betterAuth } from "better-auth";
import { createPool } from "mysql2/promise";

export const auth = betterAuth({
  database: createPool({
    host: 'localhost',
    user: 'root',
    database: 'test',
    password: process.env.MYSQL_PASSWORD
  }),
})
