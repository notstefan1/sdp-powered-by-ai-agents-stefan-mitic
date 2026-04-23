Social Network Platform Documentation
======================================

A lightweight social network where users publish short messages, follow each other,
receive an aggregated feed, get notified on @mentions, and exchange private direct messages.

.. toctree::
   :maxdepth: 2
   :caption: Overview:

   README

.. toctree::
   :maxdepth: 2
   :caption: Architecture:

   architecture/01-introduction-and-goals
   architecture/02-constraints
   architecture/03-system-scope-and-context
   architecture/04-solution-strategy
   architecture/05-building-block-view
   architecture/06-runtime-view
   architecture/07-deployment-view
   architecture/08-crosscutting-concepts
   architecture/09-architecture-decisions
   architecture/10-quality-requirements
   architecture/11-risks-and-technical-debts
   architecture/12-glossary

.. toctree::
   :maxdepth: 2
   :caption: User Stories:

   user-stories/README
   user-stories/auth
   user-stories/user-account
   user-stories/user-profile
   user-stories/user-social-graph
   user-stories/post-publishing
   user-stories/post-permalink
   user-stories/feed
   user-stories/feed-fallback
   user-stories/messaging
   user-stories/notification
   user-stories/notification-read
   user-stories/notification-recovery
   user-stories/infra-stack

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
