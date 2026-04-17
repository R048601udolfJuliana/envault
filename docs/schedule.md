# Schedule

The `schedule` command lets you configure automatic push-reminder intervals so your team is notified when the `.env` vault is overdue for a sync.

## Commands

### Set a schedule

```bash
envault schedule set 7
```

Configures a 7-day reminder interval. The schedule is stored in `.envault_schedule.json` inside the config directory.

### Show current schedule

```bash
envault schedule show
```

Prints the configured interval and when it was created.

### Check if a push is due

```bash
envault schedule check
```

Exits with code `2` if a push is due (useful in CI or git hooks), or `0` if not yet due.

### Remove a schedule

```bash
envault schedule delete
```

## Integration with hooks

You can combine `schedule check` with the `hook` command to gate commits:

```bash
# .git/hooks/pre-push
envault schedule check || echo "Reminder: sync your .env vault!"
```

## Notes

- The schedule uses the last recorded rotation timestamp from `remind` as the reference point.
- If no push has ever been recorded, the check will always return **due**.
