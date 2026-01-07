import { createAuthClient } from "better-auth/react"
import { jwtClient } from "better-auth/client/plugins"

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_APP_URL,
  plugins: [
    jwtClient()
  ]
})

export const {
  signIn,
  signOut,
  signUp,
  useSession
} = authClient;

export async function getjwt() {
  const { data, error } = await authClient.token()
  if (data) {
    const jwtToken = data.token
    return jwtToken
  }
  if (error) {
    return error
  }
}
