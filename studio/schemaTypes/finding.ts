import {defineField, defineType} from 'sanity'

export const finding = defineType({
  name: 'finding',
  title: 'Finding',
  type: 'document',
  fields: [
    defineField({
      name: 'code',
      title: 'Code',
      type: 'string',
      validation: (Rule) => Rule.required(),
      description: 'Ledger id, e.g. A1 or B9.',
    }),
    defineField({
      name: 'title',
      title: 'Title',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'foundBy',
      title: 'Found by',
      type: 'array',
      of: [{type: 'reference', to: [{type: 'person'}]}],
      validation: (Rule) => Rule.min(1),
    }),
    defineField({
      name: 'commentId',
      title: 'DEV comment ID',
      type: 'string',
      description: 'Primary comment. For multi-finder rows (B8) also fill commentIds.',
    }),
    defineField({
      name: 'commentIds',
      title: 'All comment IDs',
      type: 'array',
      of: [{type: 'string'}],
      description: 'Use when more than one comment is the finding. B8 is the reason this exists.',
    }),
    defineField({
      name: 'commentOn',
      title: 'Comment left on',
      type: 'reference',
      to: [{type: 'article'}],
      description: 'Where the stranger commented. Not where we later wrote it up.',
    }),
    defineField({
      name: 'writtenUpIn',
      title: 'Written up in',
      type: 'reference',
      to: [{type: 'article'}],
      description: 'Our article that reports the finding. B1: commentOn is 4590564, writtenUpIn is 4646467.',
    }),
    defineField({
      name: 'article',
      title: 'Article (deprecated — comment location)',
      type: 'reference',
      to: [{type: 'article'}],
      hidden: true,
      description: 'Old single field. Do not use. Maps to commentOn. Hidden so Studio cannot keep writing the mash.',
    }),
    defineField({
      name: 'status',
      title: 'Status',
      type: 'string',
      options: {
        list: [
          {title: 'Unbuilt', value: 'unbuilt'},
          {title: 'Implemented', value: 'implemented'},
          {title: 'Overlaps another row', value: 'overlaps'},
        ],
        layout: 'radio',
      },
      initialValue: 'unbuilt',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'implementedIn',
      title: 'Implemented in',
      type: 'reference',
      to: [{type: 'patch'}],
      hidden: ({document}) => document?.status !== 'implemented',
    }),
    defineField({
      name: 'overlaps',
      title: 'Overlaps',
      type: 'array',
      of: [{type: 'reference', to: [{type: 'finding'}]}],
    }),
    defineField({
      name: 'handed',
      title: 'What they handed us',
      type: 'text',
      rows: 4,
    }),
  ],
  preview: {
    select: {title: 'code', subtitle: 'status'},
  },
})
