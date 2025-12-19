import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins"
import { createPool } from "mysql2/promise";

export const auth = betterAuth({
  database: createPool({
    host: 'localhost',
    user: 'root',
    database: 'test',
    password: process.env.MYSQL_PASSWORD
  }),
  emailAndPassword: {
    enabled: true,
  },
  session: {
    cookieCache: {
      enabled: true,
      maxAge: 10 * 60 // cache duration in seconds (10 minutes)
    }
  },
  plugins: [
    jwt({
      jwks: {
        keyPairConfig: {
          alg: "EdDSA",
          crv: "Ed25519"
        }
      }
    }),
  ]
})
