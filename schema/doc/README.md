# Overview of Schema Designs


The goal of this work is to extend HydroShare’s existing resource data model to work with distributed data in the cloud. The primary focus of this work is to consolidate and simplify the implementation of how scientific metadata is stored within the HydroShare system. Our approach pivots existing functionality from reliance on a relational database to writing metadata to file(s) that are stored alongside content files. This simplifies the system and makes it easier to manage and update metadata, especially when considering distributedly hosted content.
