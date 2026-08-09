import Redis from "ioredis";
import { ENV } from "./env";

export const redisClient = new Redis(ENV.REDIS_URL);

redisClient.on("connect", () => {
  console.log("Connected to Redis");
});
