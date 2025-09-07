"""
Migration script to add admin_id column to reports table
"""
import asyncio
from sqlalchemy import text
from . import engine


async def migrate_reports_add_admin_id() -> None:
	"""Add admin_id column to reports table if it doesn't exist"""
	async with engine.begin() as conn:
		# Check if admin_id column exists
		result = await conn.execute(text("""
			SELECT COLUMN_NAME 
			FROM INFORMATION_SCHEMA.COLUMNS 
			WHERE TABLE_SCHEMA = DATABASE() 
			AND TABLE_NAME = 'reports' 
			AND COLUMN_NAME = 'admin_id'
		"""))
		
		column_exists = result.fetchone() is not None
		
		if not column_exists:
			print("Adding admin_id column to reports table...")
			await conn.execute(text("""
				ALTER TABLE reports 
				ADD COLUMN admin_id BIGINT NULL,
				ADD CONSTRAINT fk_reports_admin_id 
				FOREIGN KEY (admin_id) REFERENCES admins(id)
			"""))
			print("✅ admin_id column added successfully!")
		else:
			print("✅ admin_id column already exists!")


if __name__ == "__main__":
	asyncio.run(migrate_reports_add_admin_id())
