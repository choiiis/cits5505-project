// routes/owner.js

const express = require("express");
const router = express.Router();
const { requireRole } = require("../middleware/auth");
const db = require("../db");

// Owner: get own restaurant
router.get("/restaurant", requireRole("owner"), async (req, res) => {
  const ownerId = req.user.id;

  try {
    const restaurant = await db.get(
      "SELECT * FROM restaurants WHERE owner_id = ?",
      [ownerId]
    );

    if (!restaurant) {
      return res.status(404).json({
        error: "No restaurant found for this owner."
      });
    }

    res.json(restaurant);
  } catch (err) {
    res.status(500).json({
      error: "Failed to load restaurant information."
    });
  }
});

// Owner: update own restaurant details
router.patch("/restaurant", requireRole("owner"), async (req, res) => {
  const ownerId = req.user.id;

  const {
    name,
    address,
    cuisine,
    description,
    openingHours
  } = req.body;

  try {
    await db.run(
      `
      UPDATE restaurants
      SET name = ?, address = ?, cuisine = ?, description = ?, opening_hours = ?
      WHERE owner_id = ?
      `,
      [name, address, cuisine, description, openingHours, ownerId]
    );

    res.json({
      message: "Restaurant information updated successfully."
    });
  } catch (err) {
    res.status(500).json({
      error: "Failed to update restaurant information."
    });
  }
});

// Owner: view ratings and reviews for own restaurant
router.get("/reviews", requireRole("owner"), async (req, res) => {
  const ownerId = req.user.id;

  try {
    const restaurant = await db.get(
      "SELECT id FROM restaurants WHERE owner_id = ?",
      [ownerId]
    );

    if (!restaurant) {
      return res.status(404).json({
        error: "No restaurant found for this owner."
      });
    }

    const reviews = await db.all(
      `
      SELECT reviews.id, reviews.rating, reviews.comment, reviews.created_at, users.username
      FROM reviews
      JOIN users ON reviews.user_id = users.id
      WHERE reviews.restaurant_id = ?
      ORDER BY reviews.created_at DESC
      `,
      [restaurant.id]
    );

    res.json(reviews);
  } catch (err) {
    res.status(500).json({
      error: "Failed to load reviews."
    });
  }
});

// Owner: get average rating
router.get("/rating-summary", requireRole("owner"), async (req, res) => {
  const ownerId = req.user.id;

  try {
    const restaurant = await db.get(
      "SELECT id FROM restaurants WHERE owner_id = ?",
      [ownerId]
    );

    if (!restaurant) {
      return res.status(404).json({
        error: "No restaurant found for this owner."
      });
    }

    const result = await db.get(
      `
      SELECT 
        AVG(rating) AS averageRating,
        COUNT(*) AS reviewCount
      FROM reviews
      WHERE restaurant_id = ?
      `,
      [restaurant.id]
    );

    res.json({
      averageRating: result.averageRating || 0,
      reviewCount: result.reviewCount || 0
    });
  } catch (err) {
    res.status(500).json({
      error: "Failed to load rating summary."
    });
  }
});

module.exports = router; 