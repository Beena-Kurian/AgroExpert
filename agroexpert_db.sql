create database agroexpert
go

Use agroexpert 
Go

-- Create Users table
CREATE TABLE users (
    id INT PRIMARY KEY IDENTITY(1,1),
    username NVARCHAR(100) NOT NULL UNIQUE,
    password NVARCHAR(255) NOT NULL,
    role NVARCHAR(50) NOT NULL,
    email NVARCHAR(255) UNIQUE,
    phone NVARCHAR(20),
    status BIT DEFAULT 1,
    last_login DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create expert_details table
CREATE TABLE expert_details (
    id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT UNIQUE,
    scope NVARCHAR(255),
    specialization NVARCHAR(255),
    commodity NVARCHAR(255),
    region NVARCHAR(255),
    city NVARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Create Diseases table
CREATE TABLE diseases (
    id INT PRIMARY KEY IDENTITY(1,1),
    name NVARCHAR(255) NOT NULL,
    description TEXT,
    symptoms TEXT,
    treatment TEXT
);

-- Create Disease Predictions table
CREATE TABLE disease_predictions (
    id INT PRIMARY KEY IDENTITY(1,1),
    prediction NVARCHAR(255) NOT NULL,
    disease NVARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create Consultations table with image_path included
CREATE TABLE consultations (
    id INT PRIMARY KEY IDENTITY(1,1),
    farmer_id INT,
    expert_id INT,
    description TEXT,
    image_path NVARCHAR(255),
    plant_name NVARCHAR(255),
    symptoms TEXT,
    region NVARCHAR(255),
    date_noticed DATE,
    treatments TEXT,
    status NVARCHAR(50) DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES users (id),
    FOREIGN KEY (expert_id) REFERENCES users (id)
);

-- Create Consultation Responses table
CREATE TABLE consultation_responses (
    id INT PRIMARY KEY IDENTITY(1,1),
    consultation_id INT,
    response TEXT,
    response_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (consultation_id) REFERENCES consultations (id),
    FOREIGN KEY (response_by) REFERENCES users (id)
);

-- Create Rewards table
CREATE TABLE rewards (
    id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT,
    points INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Create Reward Transactions table
CREATE TABLE reward_transactions (
    id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT,
    amount DECIMAL(10, 2),
    transaction_type NVARCHAR(50),
    transaction_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Create Coupons table
CREATE TABLE coupons (
    id INT PRIMARY KEY IDENTITY(1,1),
    code NVARCHAR(100) UNIQUE,
    value INT,
    expiration_date DATETIME,
    is_active BIT DEFAULT 1
);

-- Create Coupon Usage table
CREATE TABLE coupon_usage (
    id INT PRIMARY KEY IDENTITY(1,1),
    coupon_id INT,
    user_id INT,
    redemption_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (coupon_id) REFERENCES coupons (id)
);

-- Create News table
CREATE TABLE news (
    id INT PRIMARY KEY IDENTITY(1,1),
    title NVARCHAR(255) NOT NULL,
    content TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create Model Versions table
CREATE TABLE model_versions (
    id INT PRIMARY KEY IDENTITY(1,1),
    model_path NVARCHAR(255) NOT NULL,
    version_number NVARCHAR(50) NOT NULL,
    accuracy FLOAT,
    total_classes INT,
    training_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    is_active BIT DEFAULT 0
);

-- Create Unknown Diseases table
CREATE TABLE unknown_diseases (
    id INT PRIMARY KEY IDENTITY(1,1),
    reported_by_farmer_id INT,
    verified_by_expert_id INT,
    initial_image_path NVARCHAR(255),
    samples_folder_path NVARCHAR(255),
    description TEXT,
    symptoms TEXT,
    date_reported DATETIME DEFAULT CURRENT_TIMESTAMP,
    status NVARCHAR(50) DEFAULT 'pending',
    admin_notes TEXT,
    FOREIGN KEY (reported_by_farmer_id) REFERENCES users (id),
    FOREIGN KEY (verified_by_expert_id) REFERENCES users (id)
);

-- Create Disease Samples table
CREATE TABLE disease_samples (
    id INT PRIMARY KEY IDENTITY(1,1),
    unknown_disease_id INT,
    farmer_id INT,
    samples_zip_path NVARCHAR(255),
    upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status NVARCHAR(50) DEFAULT 'pending',
    expert_notes TEXT,
    FOREIGN KEY (unknown_disease_id) REFERENCES unknown_diseases (id),
    FOREIGN KEY (farmer_id) REFERENCES users (id)
);

-- Create Model Classes table
CREATE TABLE model_classes (
    id INT PRIMARY KEY IDENTITY(1,1),
    class_name NVARCHAR(100) NOT NULL,
    description NVARCHAR(255)
);
