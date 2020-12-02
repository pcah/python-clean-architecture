def get_repo():
    from devops import PROJECT_PACKAGE
    import git

    assert hasattr(PROJECT_PACKAGE, "PROJECT_DIR"), "No PROJECT_DIR variable declared"
    assert PROJECT_PACKAGE.PROJECT_DIR, "No PROJECT_DIR variable injected"
    return git.Repo(PROJECT_PACKAGE.PROJECT_DIR)
