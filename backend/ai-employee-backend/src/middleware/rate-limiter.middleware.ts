import { Request, Response, NextFunction } from "express";
import { redisClient } from "../config/redis";

export const rateLimiter = async (req: Request, res: Response, next: NextFunction) => {
  const ip = req.ip || "unknown";
  const key = `rate:${ip}`;
  const count = await redisClient.incr(key);

  if (count === 1) {
    await redisClient.expire(key, 60);
  }

  if (count > 100) {
    return res.status(429).json({ message: "Too many requests" });
  }

  next();
};
